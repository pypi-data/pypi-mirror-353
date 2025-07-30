use rust_decimal::prelude::*;
use serde::Serialize;
use std::{convert::Infallible, str::FromStr};

use crate::utils::{split_letter_number_pairs, split_value_unit};
#[derive(Debug, PartialEq, Eq, Default, Clone, Serialize)]
pub struct AdditionalPrecision {
    pub lat: u8,
    pub lon: u8,
}

#[derive(Debug, PartialEq, Eq, Default, Clone, Serialize)]
pub struct ID {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reserved: Option<u16>,
    pub address_type: u16,
    pub aircraft_type: u8,
    pub is_stealth: bool,
    pub is_notrack: bool,
    pub address: u32,
}

#[derive(Debug, PartialEq, Default, Clone, Serialize)]
pub struct PositionComment {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub course: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub speed: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub altitude: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub wind_direction: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub wind_speed: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gust: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<i16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rainfall_1h: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rainfall_24h: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rainfall_midnight: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub humidity: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub barometric_pressure: Option<u32>,
    #[serde(skip_serializing)]
    pub additional_precision: Option<AdditionalPrecision>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(flatten)]
    pub id: Option<ID>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub climb_rate: Option<i16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub turn_rate: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signal_quality: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub frequency_offset: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gps_quality: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub flight_level: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signal_power: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub software_version: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hardware_version: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub original_address: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub unparsed: Option<String>,
}

impl FromStr for PositionComment {
    type Err = Infallible;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut position_comment = PositionComment {
            ..Default::default()
        };
        let mut unparsed: Vec<_> = vec![];
        for (idx, part) in s.split_ascii_whitespace().enumerate() {
            // The first part can be course + speed + altitude: ccc/sss/A=aaaaaa
            // ccc: course in degrees 0-360
            // sss: speed in km/h
            // aaaaaa: altitude in feet
            if idx == 0
                && part.len() == 16
                && &part[3..4] == "/"
                && &part[7..10] == "/A="
                && position_comment.course.is_none()
            {
                let course = part[0..3].parse::<u16>().ok();
                let speed = part[4..7].parse::<u16>().ok();
                let altitude = part[10..16].parse::<u32>().ok();
                if course.is_some()
                    && course.unwrap() <= 360
                    && speed.is_some()
                    && altitude.is_some()
                {
                    position_comment.course = course;
                    position_comment.speed = speed;
                    position_comment.altitude = altitude;
                } else {
                    unparsed.push(part);
                }
            // ... or just the altitude: /A=aaaaaa
            // aaaaaa: altitude in feet
            } else if idx == 0
                && part.len() == 9
                && &part[0..3] == "/A="
                && position_comment.altitude.is_none()
            {
                match part[3..].parse::<u32>().ok() {
                    Some(altitude) => position_comment.altitude = Some(altitude),
                    None => unparsed.push(part),
                }
            // ... or a complete weather report: ccc/sss/XXX...
            // starting ccc/sss is now wind_direction and wind_speed
            // XXX... is a string of data pairs, where each pair has one letter that indicates the type of data and a number that indicates the value
            //
            // mandatory fields:
            // gddd: gust (peak wind speed in mph in the last 5 minutes)
            // tddd: temperature (in degrees Fahrenheit). Temperatures below zero are expressed as -01 to -99
            //
            // optional fields:
            // rddd: rainfall (in hundrets of inches) in the last hour
            // pddd: rainfall (in hundrets of inches) in the last 24 hours
            // Pddd: rainfall (in hundrets of inches) since midnight
            // hdd: humidity (in % where 00 is 100%)
            // bddddd: barometric pressure (in tenths of millibars/tenths of hPascal)
            } else if idx == 0
                && part.len() >= 15
                && &part[3..4] == "/"
                && position_comment.wind_direction.is_none()
            {
                let wind_direction = part[0..3].parse::<u16>().ok();
                let wind_speed = part[4..7].parse::<u16>().ok();

                if wind_direction.is_some() && wind_speed.is_some() {
                    position_comment.wind_direction = wind_direction;
                    position_comment.wind_speed = wind_speed;
                } else {
                    unparsed.push(part);
                    continue;
                }

                let pairs = split_letter_number_pairs(&part[7..]);

                // check if any type of data is not in the allowed set or if any type is duplicated
                let mut seen = std::collections::HashSet::new();
                if pairs
                    .iter()
                    .any(|(c, _)| !seen.insert(*c) || !"gtrpPhb".contains(*c))
                {
                    unparsed.push(part);
                    continue;
                }

                for (c, number) in pairs {
                    match c {
                        'g' => position_comment.gust = Some(number as u16),
                        't' => position_comment.temperature = Some(number as i16),
                        'r' => position_comment.rainfall_1h = Some(number as u16),
                        'p' => position_comment.rainfall_24h = Some(number as u16),
                        'P' => position_comment.rainfall_midnight = Some(number as u16),
                        'h' => position_comment.humidity = Some(number as u8),
                        'b' => position_comment.barometric_pressure = Some(number as u32),
                        _ => unreachable!(),
                    }
                }
            // The second part can be the additional precision: !Wab!
            // a: additional latitude precision
            // b: additional longitude precision
            } else if idx == 1
                && part.len() == 5
                && &part[0..2] == "!W"
                && &part[4..] == "!"
                && position_comment.additional_precision.is_none()
            {
                let add_lat = part[2..3].parse::<u8>().ok();
                let add_lon = part[3..4].parse::<u8>().ok();
                match (add_lat, add_lon) {
                    (Some(add_lat), Some(add_lon)) => {
                        position_comment.additional_precision = Some(AdditionalPrecision {
                            lat: add_lat,
                            lon: add_lon,
                        })
                    }
                    _ => unparsed.push(part),
                }
            // generic ID format: idXXYYYYYY (4 bytes format)
            // YYYYYY: 24 bit address in hex digits
            // XX in hex digits encodes stealth mode, no-tracking flag and address type
            // XX to binary-> STtt ttaa
            // S: stealth flag
            // T: no-tracking flag
            // tttt: aircraft type
            // aa: address type
            } else if part.len() == 10 && &part[0..2] == "id" && position_comment.id.is_none() {
                if let (Some(detail), Some(address)) = (
                    u8::from_str_radix(&part[2..4], 16).ok(),
                    u32::from_str_radix(&part[4..10], 16).ok(),
                ) {
                    let address_type = (detail & 0b0000_0011) as u16;
                    let aircraft_type = (detail & 0b_0011_1100) >> 2;
                    let is_notrack = (detail & 0b0100_0000) != 0;
                    let is_stealth = (detail & 0b1000_0000) != 0;
                    position_comment.id = Some(ID {
                        address_type,
                        aircraft_type,
                        is_notrack,
                        is_stealth,
                        address,
                        ..Default::default()
                    });
                } else {
                    unparsed.push(part);
                }
            // NAVITER ID format: idXXXXYYYYYY (5 bytes)
            // YYYYYY: 24 bit address in hex digits
            // XXXX in hex digits encodes stealth mode, no-tracking flag and address type
            // XXXX to binary-> STtt ttaa aaaa rrrr
            // S: stealth flag
            // T: no-tracking flag
            // tttt: aircraft type
            // aaaaaa: address type
            // rrrr: (reserved)
            } else if part.len() == 12 && &part[0..2] == "id" && position_comment.id.is_none() {
                if let (Some(detail), Some(address)) = (
                    u16::from_str_radix(&part[2..6], 16).ok(),
                    u32::from_str_radix(&part[6..12], 16).ok(),
                ) {
                    let reserved = detail & 0b0000_0000_0000_1111;
                    let address_type = (detail & 0b0000_0011_1111_0000) >> 4;
                    let aircraft_type = ((detail & 0b0011_1100_0000_0000) >> 10) as u8;
                    let is_notrack = (detail & 0b0100_0000_0000_0000) != 0;
                    let is_stealth = (detail & 0b1000_0000_0000_0000) != 0;
                    position_comment.id = Some(ID {
                        reserved: Some(reserved),
                        address_type,
                        aircraft_type,
                        is_notrack,
                        is_stealth,
                        address,
                    });
                } else {
                    unparsed.push(part);
                }
            } else if let Some((value, unit)) = split_value_unit(part) {
                if unit == "fpm" && position_comment.climb_rate.is_none() {
                    position_comment.climb_rate = value.parse::<i16>().ok();
                } else if unit == "rot" && position_comment.turn_rate.is_none() {
                    position_comment.turn_rate =
                        value.parse::<f32>().ok().and_then(Decimal::from_f32);
                } else if unit == "dB" && position_comment.signal_quality.is_none() {
                    position_comment.signal_quality =
                        value.parse::<f32>().ok().and_then(Decimal::from_f32);
                } else if unit == "kHz" && position_comment.frequency_offset.is_none() {
                    position_comment.frequency_offset =
                        value.parse::<f32>().ok().and_then(Decimal::from_f32);
                } else if unit == "e" && position_comment.error.is_none() {
                    position_comment.error = value.parse::<u8>().ok();
                } else if unit == "dBm" && position_comment.signal_power.is_none() {
                    position_comment.signal_power =
                        value.parse::<f32>().ok().and_then(Decimal::from_f32);
                } else {
                    unparsed.push(part);
                }
            // Gps precision: gpsAxB
            // A: integer
            // B: integer
            } else if part.len() >= 6
                && &part[0..3] == "gps"
                && position_comment.gps_quality.is_none()
            {
                if let Some((first, second)) = part[3..].split_once('x') {
                    if first.parse::<u8>().is_ok() && second.parse::<u8>().is_ok() {
                        position_comment.gps_quality = Some(part[3..].to_string());
                    } else {
                        unparsed.push(part);
                    }
                } else {
                    unparsed.push(part);
                }
            // Flight level: FLxx.yy
            // xx.yy: float value for flight level
            } else if part.len() >= 3
                && &part[0..2] == "FL"
                && position_comment.flight_level.is_none()
            {
                if let Ok(flight_level) = part[2..].parse::<f32>() {
                    position_comment.flight_level = Decimal::from_f32(flight_level);
                } else {
                    unparsed.push(part);
                }
            // Software version: sXX.YY
            // XX.YY: float value for software version
            } else if part.len() >= 2
                && &part[0..1] == "s"
                && position_comment.software_version.is_none()
            {
                if let Ok(software_version) = part[1..].parse::<f32>() {
                    position_comment.software_version = Decimal::from_f32(software_version);
                } else {
                    unparsed.push(part);
                }
            // Hardware version: hXX
            // XX: hexadecimal value for hardware version
            } else if part.len() == 3
                && &part[0..1] == "h"
                && position_comment.hardware_version.is_none()
            {
                if part[1..3].chars().all(|c| c.is_ascii_hexdigit()) {
                    position_comment.hardware_version = u8::from_str_radix(&part[1..3], 16).ok();
                } else {
                    unparsed.push(part);
                }
            // Original address: rXXXXXX
            // XXXXXX: hex digits for 24 bit address
            } else if part.len() == 7
                && &part[0..1] == "r"
                && position_comment.original_address.is_none()
            {
                if part[1..7].chars().all(|c| c.is_ascii_hexdigit()) {
                    position_comment.original_address = u32::from_str_radix(&part[1..7], 16).ok();
                } else {
                    unparsed.push(part);
                }
            } else {
                unparsed.push(part);
            }
        }
        position_comment.unparsed = if !unparsed.is_empty() {
            Some(unparsed.join(" "))
        } else {
            None
        };

        Ok(position_comment)
    }
}

#[test]
fn test_flr() {
    let result = "255/045/A=003399 !W03! id06DDFAA3 -613fpm -3.9rot 22.5dB 7e -7.0kHz gps3x7 s7.07 h41 rD002F8".parse::<PositionComment>().unwrap();
    assert_eq!(
        result,
        PositionComment {
            course: Some(255),
            speed: Some(45),
            altitude: Some(3399),
            additional_precision: Some(AdditionalPrecision { lat: 0, lon: 3 }),
            id: Some(ID {
                reserved: None,
                address_type: 2,
                aircraft_type: 1,
                is_stealth: false,
                is_notrack: false,
                address: u32::from_str_radix("DDFAA3", 16).unwrap(),
            }),
            climb_rate: Some(-613),
            turn_rate: Decimal::from_f32(-3.9),
            signal_quality: Decimal::from_f32(22.5),
            error: Some(7),
            frequency_offset: Decimal::from_f32(-7.0),
            gps_quality: Some("3x7".into()),
            software_version: Decimal::from_f32(7.07),
            hardware_version: Some(65),
            original_address: u32::from_str_radix("D002F8", 16).ok(),
            ..Default::default()
        }
    );
}

#[test]
fn test_trk() {
    let result =
        "200/073/A=126433 !W05! id15B50BBB +4237fpm +2.2rot FL1267.81 10.0dB 19e +23.8kHz gps36x55"
            .parse::<PositionComment>()
            .unwrap();
    assert_eq!(
        result,
        PositionComment {
            course: Some(200),
            speed: Some(73),
            altitude: Some(126433),
            wind_direction: None,
            wind_speed: None,
            gust: None,
            temperature: None,
            rainfall_1h: None,
            rainfall_24h: None,
            rainfall_midnight: None,
            humidity: None,
            barometric_pressure: None,
            additional_precision: Some(AdditionalPrecision { lat: 0, lon: 5 }),
            id: Some(ID {
                address_type: 1,
                aircraft_type: 5,
                is_stealth: false,
                is_notrack: false,
                address: u32::from_str_radix("B50BBB", 16).unwrap(),
                ..Default::default()
            }),
            climb_rate: Some(4237),
            turn_rate: Decimal::from_f32(2.2),
            signal_quality: Decimal::from_f32(10.0),
            error: Some(19),
            frequency_offset: Decimal::from_f32(23.8),
            gps_quality: Some("36x55".into()),
            flight_level: Decimal::from_f32(1267.81),
            signal_power: None,
            software_version: None,
            hardware_version: None,
            original_address: None,
            unparsed: None
        }
    );
}

#[test]
fn test_trk2() {
    let result = "000/000/A=002280 !W59! id07395004 +000fpm +0.0rot FL021.72 40.2dB -15.1kHz gps9x13 +15.8dBm".parse::<PositionComment>().unwrap();
    assert_eq!(
        result,
        PositionComment {
            course: Some(0),
            speed: Some(0),
            altitude: Some(2280),
            additional_precision: Some(AdditionalPrecision { lat: 5, lon: 9 }),
            id: Some(ID {
                address_type: 3,
                aircraft_type: 1,
                is_stealth: false,
                is_notrack: false,
                address: u32::from_str_radix("395004", 16).unwrap(),
                ..Default::default()
            }),
            climb_rate: Some(0),
            turn_rate: Decimal::from_f32(0.0),
            signal_quality: Decimal::from_f32(40.2),
            frequency_offset: Decimal::from_f32(-15.1),
            gps_quality: Some("9x13".into()),
            flight_level: Decimal::from_f32(21.72),
            signal_power: Decimal::from_f32(15.8),
            ..Default::default()
        }
    );
}

#[test]
fn test_trk2_different_order() {
    // Check if order doesn't matter
    let result = "000/000/A=002280 !W59! -15.1kHz id07395004 +15.8dBm +0.0rot +000fpm FL021.72 40.2dB gps9x13".parse::<PositionComment>().unwrap();
    assert_eq!(
        result,
        PositionComment {
            course: Some(0),
            speed: Some(0),
            altitude: Some(2280),
            additional_precision: Some(AdditionalPrecision { lat: 5, lon: 9 }),
            id: Some(ID {
                address_type: 3,
                aircraft_type: 1,
                is_stealth: false,
                is_notrack: false,
                address: u32::from_str_radix("395004", 16).unwrap(),
                ..Default::default()
            }),
            climb_rate: Some(0),
            turn_rate: Decimal::from_f32(0.0),
            signal_quality: Decimal::from_f32(40.2),
            frequency_offset: Decimal::from_f32(-15.1),
            gps_quality: Some("9x13".into()),
            flight_level: Decimal::from_f32(21.72),
            signal_power: Decimal::from_f32(15.8),
            ..Default::default()
        }
    );
}

#[test]
fn test_bad_gps() {
    let result = "208/063/A=003222 !W97! id06D017DC -395fpm -2.4rot 8.2dB -6.1kHz gps2xFLRD0"
        .parse::<PositionComment>()
        .unwrap();
    assert_eq!(result.frequency_offset, Decimal::from_f32(-6.1));
    assert_eq!(result.gps_quality.is_some(), false);
    assert_eq!(result.unparsed, Some("gps2xFLRD0".to_string()));
}

#[test]
fn test_naviter_id() {
    let result = "000/000/A=000000 !W0! id985F579BDF"
        .parse::<PositionComment>()
        .unwrap();
    assert_eq!(result.id.is_some(), true);
    let id = result.id.unwrap();

    assert_eq!(id.reserved, Some(15));
    assert_eq!(id.address_type, 5);
    assert_eq!(id.aircraft_type, 6);
    assert_eq!(id.is_stealth, true);
    assert_eq!(id.is_notrack, false);
    assert_eq!(id.address, 0x579BDF);
}

#[test]
fn parse_weather() {
    let result = "187/004g007t075h78b63620"
        .parse::<PositionComment>()
        .unwrap();
    assert_eq!(result.wind_direction, Some(187));
    assert_eq!(result.wind_speed, Some(4));
    assert_eq!(result.gust, Some(7));
    assert_eq!(result.temperature, Some(75));
    assert_eq!(result.humidity, Some(78));
    assert_eq!(result.barometric_pressure, Some(63620));
}

#[test]
fn parse_weather_bad_type() {
    let result = "187/004g007X075h78b63620"
        .parse::<PositionComment>()
        .unwrap();
    assert_eq!(
        result.unparsed,
        Some("187/004g007X075h78b63620".to_string())
    );
}

#[test]
fn parse_weather_duplicate_type() {
    let result = "187/004g007t075g78b63620"
        .parse::<PositionComment>()
        .unwrap();
    assert_eq!(
        result.unparsed,
        Some("187/004g007t075g78b63620".to_string())
    );
}
