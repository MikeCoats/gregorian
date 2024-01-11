#!/usr/bin/env python
"""The Greg or Ian Calendar.

A web app, API and RFC5545 iCalendar feed to determine whether today is a "Greg" or an
"Ian" day.

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Affero General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this
program.  If not, see <http://www.gnu.org/licenses/>.
"""

__copyright__ = "Copyright (C) 2024  Mike Coats"
__license__ = "AGPL-3.0-or-later"
__contact__ = "i.am@mikecoats.com"

__author__ = "Mike Coats"
__credits__ = ["Mike Coats", "Natasha Jay", "Khomsun Chaiwong"]

__maintainer__ = "Mike Coats"
__email__ = "i.am@mikecoats.com"

__status__ = "Production"
__version__ = "1.1.2"

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
    """Used to tell FastAPI to return the response with a 'text/calendar' media type.

    This class is cribbed directly from FastAPI's HTMLResponse, which is simply:

    ```
    class HTMLResponse(Response):
        media_type = "text/html"
    ```
    """

    media_type = "text/calendar"


app = FastAPI()
templates = Jinja2Templates(directory=".")
app.mount("/assets", StaticFiles(directory="./assets"), name="assets")


def day_ordinal(day: int):
    """Return whether a day of the month is a 'st', 'nd', 'rd' or 'th'."""
    if day in (1, 21, 31):
        return "st"
    if day in (2, 22):
        return "nd"
    if day in (3, 23):
        return "rd"
    return "th"


def pretty_date(src: date):
    """Serialize a date in the format 'Sunday, 5th May 2024'."""
    day_of_month = src.day
    pretty_day = f"{day_of_month}{day_ordinal(day_of_month)}"
    return src.strftime(f"%A, {pretty_day} %B %Y")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Return an HTML page so our visitor knows today's 'Greg' or 'Ian' status."""
    today = date.today()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "date": today.strftime("%Y-%m-%d"),
            "nice_date": pretty_date(today),
            "greg_or_ian": GREG_OR_IAN[today.weekday()],
        },
    )


def build_event(src_date: date, offset_days: int):
    """Return an all-day Event, captioned with Greg or Ian."""
    offset = timedelta(days=offset_days)
    event_date = src_date + offset
    e = Event(begin=event_date, name=GREG_OR_IAN[event_date.weekday()])
    e.make_all_day()
    return e


@app.get("/feed.ics", response_class=CalendarResponse)
async def feed():
    """Return an iCal feed so our visitor knows many 'Greg' or 'Ian' statuses."""
    today = date.today()
    c = Calendar(events=[build_event(today, offset) for offset in range(-7, 28)])
    return c.serialize()


async def main():
    """When the module is run directly, hook up a uvicorn server and host the app."""
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
