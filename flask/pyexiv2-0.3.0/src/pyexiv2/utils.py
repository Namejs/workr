# -*- coding: utf-8 -*-

# ******************************************************************************
#
# Copyright (C) 2006-2010 Olivier Tilloy <olivier@tilloy.net>
#
# This file is part of the pyexiv2 distribution.
#
# pyexiv2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# pyexiv2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyexiv2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, 5th Floor, Boston, MA 02110-1301 USA.
#
# Author: Olivier Tilloy <olivier@tilloy.net>
#
# ******************************************************************************

"""
Utilitary classes and functions.
"""

import datetime
import re

# pyexiv2 uses fractions.Fraction when available (Python ≥ 2.6), or falls back
# on the custom Rational class. This should be transparent to the application
# developer as both classes have a similar API.
# This module contains convenience functions to ease manipulation of fractions.
try:
    from fractions import Fraction
except ImportError:
    Fraction = None


class FixedOffset(datetime.tzinfo):

    """
    Fixed positive or negative offset from a local time east from UTC.

    :attribute sign: the sign of the offset ('+' or '-')
    :type sign: string
    :attribute hours: the absolute number of hours of the offset
    :type hours: int
    :attribute minutes: the absolute number of minutes of the offset
    :type minutes: int
    """

    def __init__(self, sign='+', hours=0, minutes=0):
        """
        Initialize an offset from a sign ('+' or '-') and an absolute value
        expressed in hours and minutes.
        No check on the validity of those values is performed, it is the
        responsibility of the caller to pass valid values.

        :param sign: the sign of the offset ('+' or '-')
        :type sign: string
        :param hours: an absolute number of hours
        :type hours: int
        :param minutes: an absolute number of minutes
        :type minutes: int
        """
        self.sign = sign
        self.hours = hours
        self.minutes = minutes

    def utcoffset(self, dt):
        """
        Return offset of local time from UTC, in minutes east of UTC.
        If local time is west of UTC, this value will be negative.

        :param dt: the local time
        :type dt: :class:`datetime.time`

        :return: a whole number of minutes in the range -1439 to 1439 inclusive
        :rtype: :class:`datetime.timedelta`
        """
        total = self.hours * 60 + self.minutes
        if self.sign == '-':
            total = -total
        return datetime.timedelta(minutes = total)

    def dst(self, dt):
        """
        Return the daylight saving time (DST) adjustment.
        In this implementation, it is always nil.

        :param dt: the local time
        :type dt: :class:`datetime.time`

        :return: the DST adjustment (always nil)
        :rtype: :class:`datetime.timedelta`
        """
        return datetime.timedelta(0)

    def tzname(self, dt):
        """
        Return a string representation of the offset in the format '±%H:%M'.
        If the offset is nil, the representation is, by convention, 'Z'.

        :param dt: the local time
        :type dt: :class:`datetime.time`

        :return: a human-readable representation of the offset
        :rtype: string
        """
        if self.hours == 0 and self.minutes == 0:
            return 'Z'
        else:
            return '%s%02d:%02d' % (self.sign, self.hours, self.minutes)

    def __equal__(self, other):
        """
        Test equality between this offset and another offset.

        :param other: another offset
        :type other: :class:`FixedOffset`

        :return: True if the offset are equal, False otherwise
        :rtype: boolean
        """
        return (self.sign == other.sign) and (self.hours == other.hours) and \
            (self.minutes == other.minutes)


def undefined_to_string(undefined):
    """
    Convert an undefined string into its corresponding sequence of bytes.
    The undefined string must contain the ascii codes of a sequence of bytes,
    separated by white spaces (e.g. "48 50 50 49" will be converted into
    "0221").
    The Undefined type is part of the EXIF specification.

    :param undefined: an undefined string
    :type undefined: string

    :return: the corresponding decoded string
    :rtype: string
    """
    return ''.join(map(lambda x: chr(int(x)), undefined.rstrip().split(' ')))


def string_to_undefined(sequence):
    """
    Convert a string into its undefined form.
    The undefined form contains a sequence of ascii codes separated by white
    spaces (e.g. "0221" will be converted into "48 50 50 49").
    The Undefined type is part of the EXIF specification.

    :param sequence: a sequence of bytes
    :type sequence: string

    :return: the corresponding undefined string
    :rtype: string
    """
    return ''.join(map(lambda x: '%d ' % ord(x), sequence)).rstrip()


class Rational(object):

    """
    A class representing a rational number.

    Its numerator and denominator are read-only properties.
    """

    _format_re = re.compile(r'(?P<numerator>-?\d+)/(?P<denominator>\d+)')

    def __init__(self, numerator, denominator):
        """
        :param numerator: the numerator
        :type numerator: long
        :param denominator: the denominator
        :type denominator: long

        :raise ZeroDivisionError: if the denominator equals zero
        """
        if denominator == 0:
            msg = 'Denominator of a rational number cannot be zero.'
            raise ZeroDivisionError(msg)
        self._numerator = long(numerator)
        self._denominator = long(denominator)

    @property
    def numerator(self):
        """The numerator of the rational number."""
        return self._numerator

    @property
    def denominator(self):
        """The denominator of the rational number."""
        return self._denominator

    @staticmethod
    def from_string(string):
        """
        Instantiate a :class:`Rational` from a string formatted as
        ``[-]numerator/denominator``.

        :param string: a string representation of a rational number
        :type string: string

        :return: the rational number parsed
        :rtype: :class:`Rational`

        :raise ValueError: if the format of the string is invalid
        """
        match = Rational._format_re.match(string)
        if match is None:
            raise ValueError('Invalid format for a rational: %s' % string)
        gd = match.groupdict()
        return Rational(long(gd['numerator']), long(gd['denominator']))

    def to_float(self):
        """
        :return: a floating point number approximation of the value
        :rtype: float
        """
        return float(self._numerator) / self._denominator

    def __eq__(self, other):
        """
        Compare two rational numbers for equality.

        Two rational numbers are equal if their reduced forms are equal.

        :param other: the rational number to compare to self for equality
        :type other: :class:`Rational`
        
        :return: True if equal, False otherwise
        :rtype: boolean
        """
        return (self._numerator * other._denominator) == \
               (other._numerator * self._denominator)

    def __str__(self):
        """
        :return: a string representation of the rational number
        :rtype: string
        """
        return '%d/%d' % (self._numerator, self._denominator)


def is_fraction(obj):
    """
    Test whether the object is a valid fraction.
    """
    if Fraction is not None and isinstance(obj, Fraction):
        return True
    elif isinstance(obj, Rational):
        return True
    else:
        return False


def make_fraction(*args):
    """
    Make a fraction.

    The type of the returned object depends on the availability of the
    fractions module in the standard library (Python ≥ 2.6).
    """
    if Fraction is not None:
        return Fraction(*args)
    else:
        if len(args) == 1:
            return Rational.from_string(*args)
        else:
            return Rational(*args)


def fraction_to_string(fraction):
    """
    Return a string representation of a fraction, suitable to pass to libexiv2.

    The returned string is always in the form '[numerator]/[denominator]'.

    :raise TypeError: if the argument is not a valid fraction
    """
    if Fraction is not None and isinstance(fraction, Fraction):
        # fractions.Fraction.__str__ returns '0' for a null numerator.
        return '%s/%s' % (fraction.numerator, fraction.denominator)
    elif isinstance(fraction, Rational):
        return str(fraction)
    else:
        raise TypeError('Not a fraction')


class ListenerInterface(object):

    """
    Interface that an object that wants to listen to changes on another object
    should implement.
    """

    def contents_changed(self):
        """
        React on changes on the object observed.
        Override to implement specific behaviours.
        """
        raise NotImplementedError()


class NotifyingList(list):

    """
    A simplistic implementation of a notifying list.
    Any changes to the list are notified in a synchronous way to all previously
    registered listeners. A listener must implement the
    :class:`ListenerInterface`.
    """

    # Useful documentation:
    # file:///usr/share/doc/python2.5/html/lib/typesseq-mutable.html
    # http://docs.python.org/reference/datamodel.html#additional-methods-for-emulation-of-sequence-types

    def __init__(self, items=[]):
        super(NotifyingList, self).__init__(items)
        self._listeners = set()

    def register_listener(self, listener):
        """
        Register a new listener to be notified of changes.

        :param listener: any object that listens for changes
        :type listener: :class:`ListenerInterface`
        """
        self._listeners.add(listener)

    def unregister_listener(self, listener):
        """
        Unregister a previously registered listener.

        :param listener: a previously registered listener
        :type listener: :class:`ListenerInterface`

        :raise KeyError: if the listener was not previously registered
        """
        self._listeners.remove(listener)

    def _notify_listeners(self, *args):
        for listener in self._listeners:
            listener.contents_changed(*args)

    def __setitem__(self, index, item):
        # FIXME: support slice arguments for extended slicing
        super(NotifyingList, self).__setitem__(index, item)
        self._notify_listeners()

    def __delitem__(self, index):
        # FIXME: support slice arguments for extended slicing
        super(NotifyingList, self).__delitem__(index)
        self._notify_listeners()

    def append(self, item):
        super(NotifyingList, self).append(item)
        self._notify_listeners()

    def extend(self, items):
        super(NotifyingList, self).extend(items)
        self._notify_listeners()

    def insert(self, index, item):
        super(NotifyingList, self).insert(index, item)
        self._notify_listeners()

    def pop(self, index=None):
        if index is None:
            item = super(NotifyingList, self).pop()
        else:
            item = super(NotifyingList, self).pop(index)
        self._notify_listeners()
        return item

    def remove(self, item):
        super(NotifyingList, self).remove(item)
        self._notify_listeners()

    def reverse(self):
        super(NotifyingList, self).reverse()
        self._notify_listeners()

    def sort(self, cmp=None, key=None, reverse=False):
        super(NotifyingList, self).sort(cmp, key, reverse)
        self._notify_listeners()

    def __iadd__(self, other):
        self = super(NotifyingList, self).__iadd__(other)
        self._notify_listeners()
        return self

    def __imul__(self, coefficient):
        self = super(NotifyingList, self).__imul__(coefficient)
        self._notify_listeners()
        return self

    def __setslice__(self, i, j, items):
        # __setslice__ is deprecated but needs to be overridden for completeness
        super(NotifyingList, self).__setslice__(i, j, items)
        self._notify_listeners()

    def __delslice__(self, i, j):
        # __delslice__ is deprecated but needs to be overridden for completeness
        deleted = self[i:j]
        super(NotifyingList, self).__delslice__(i, j)
        if deleted:
            self._notify_listeners()


class GPSCoordinate(object):

    """
    A class representing GPS coordinates (e.g. a latitude or a longitude).

    Its attributes (degrees, minutes, seconds, direction) are read-only
    properties.
    """

    _format_re = \
        re.compile(r'(?P<degrees>-?\d+),'
                    '(?P<minutes>\d+)(,(?P<seconds>\d+)|\.(?P<fraction>\d+))'
                    '(?P<direction>[NSEW])')

    def __init__(self, degrees, minutes, seconds, direction):
        """
        :param degrees: degrees
        :type degrees: int
        :param minutes: minutes
        :type minutes: int
        :param seconds: seconds
        :type seconds: int
        :param direction: direction ('N', 'S', 'E' or 'W')
        :type direction: string

        :raise ValueError: if any of the parameter is not in the expected range
                           of values
        """
        if direction not in ('N', 'S', 'E', 'W'):
            raise ValueError('Invalid direction: %s' % direction)
        self._direction = direction
        if (direction in ('N', 'S') and (degrees < 0 or degrees > 90)) or \
           (direction in ('E', 'W') and (degrees < 0 or degrees > 180)):
            raise ValueError('Invalid value for degrees: %d' % degrees)
        self._degrees = degrees
        if minutes < 0 or minutes > 60:
            raise ValueError('Invalid value for minutes: %d' % minutes)
        self._minutes = minutes
        if seconds < 0 or seconds > 60:
            raise ValueError('Invalid value for seconds: %d' % seconds)
        self._seconds = seconds

    @property
    def degrees(self):
        """The degrees component of the coordinate."""
        return self._degrees

    @property
    def minutes(self):
        """The minutes component of the coordinate."""
        return self._minutes

    @property
    def seconds(self):
        """The seconds component of the coordinate."""
        return self._seconds

    @property
    def direction(self):
        """The direction component of the coordinate."""
        return self._direction

    @staticmethod
    def from_string(string):
        """
        Instantiate a :class:`GPSCoordinate` from a string formatted as
        ``DDD,MM,SSk`` or ``DDD,MM.mmk`` where ``DDD`` is a number of degrees,
        ``MM`` is a number of minutes, ``SS`` is a number of seconds, ``mm`` is
        a fraction of minutes, and ``k`` is a single character N, S, E, W
        indicating a direction (north, south, east, west).

        :param string: a string representation of a GPS coordinate
        :type string: string

        :return: the GPS coordinate parsed
        :rtype: :class:`GPSCoordinate`

        :raise ValueError: if the format of the string is invalid
        """
        match = GPSCoordinate._format_re.match(string)
        if match is None:
            raise ValueError('Invalid format for a GPS coordinate: %s' % string)
        gd = match.groupdict()
        fraction = gd['fraction']
        if fraction is not None:
            seconds = int(round(int(fraction[:2]) * 0.6))
        else:
            seconds = int(gd['seconds'])
        return GPSCoordinate(int(gd['degrees']), int(gd['minutes']), seconds,
                             gd['direction'])

    def __eq__(self, other):
        """
        Compare two GPS coordinates for equality.

        Two coordinates are equal if and only if all their components are equal.

        :param other: the GPS coordinate to compare to self for equality
        :type other: :class:`GPSCoordinate`

        :return: True if equal, False otherwise
        :rtype: boolean
        """
        return (self._degrees == other._degrees) and \
               (self._minutes == other._minutes) and \
               (self._seconds == other._seconds) and \
               (self._direction == other._direction)

    def __str__(self):
        """
        :return: a string representation of the GPS coordinate conforming to the
                 XMP specification
        :rtype: string
        """
        return '%d,%d,%d%s' % (self._degrees, self._minutes, self._seconds,
                               self._direction)

