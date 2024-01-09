#!/usr/bin/env python
"""The Greg or Ian Calendar.

A web app, API and RFC5545 iCalendar feed to determine whether today is
a "Greg" or an "Ian" day.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__copyright__ = "Copyright (C) 2024  Mike Coats"
__license__ = "AGPL-3.0-or-later"
__contact__ = "i.am@mikecoats.com"

__author__ = "Mike Coats"
__credits__ = ["Mike Coats", "Natasha Jay", "Khomsun Chaiwong"]

__maintainer__ = "Mike Coats"
__email__ = "i.am@mikecoats.com"

__status__ = "Production"
__version__ = "1.0.0"

import asyncio
from datetime import date, timedelta

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ics import Calendar, Event


GREG = "Greg"
IAN = "Ian"

GREG_OR_IAN = [
    GREG,
    IAN,
    GREG,
    IAN,
    GREG,
    IAN,
    GREG,
]


class CalendarResponse(Response):
    media_type = "text/calendar"


app = FastAPI()
templates = Jinja2Templates(directory=".")
app.mount("/assets", StaticFiles(directory="./assets"), name="assets")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    today = date.today()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "date": today.strftime('%Y-%m-%d'),
            "nice_date": today.strftime('%A, %d %B %Y'.format()), #"Tuesday, 9th January 2024",
            "greg_or_ian": GREG_OR_IAN[today.weekday()],
        },
    )


@app.get("/feed.ics", response_class=CalendarResponse)
async def feed():
    c = Calendar()
    today = date.today()
    for i in range(-7, 28):
        offset_days = timedelta(days=i)
        event_date = today + offset_days
        e = Event(begin=event_date, name=GREG_OR_IAN[event_date.weekday()])
        e.make_all_day()
        c.events.add(e)
    return c.serialize()


async def main():
    """When the module is run directly, hook up a uvicorn server and
    host the app.
    """
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
