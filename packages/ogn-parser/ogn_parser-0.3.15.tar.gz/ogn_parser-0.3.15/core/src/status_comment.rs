use rust_decimal::prelude::*;
use serde::Serialize;
use std::{convert::Infallible, str::FromStr};

use crate::utils::{extract_values, split_value_unit};

#[derive(Debug, PartialEq, Default, Clone, Serialize)]
pub struct StatusComment {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub platform: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cpu_load: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ram_free: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ram_total: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ntp_offset: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ntp_correction: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub voltage: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub amperage: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cpu_temperature: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub visible_senders: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub latency: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub senders: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rf_correction_manual: Option<i16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rf_correction_automatic: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub noise: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub senders_signal_quality: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub senders_messages: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub good_senders_signal_quality: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub good_senders: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub good_and_bad_senders: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub unparsed: Option<String>,
}

impl FromStr for StatusComment {
    type Err = Infallible;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut status_comment = StatusComment {
            ..Default::default()
        };
        let mut unparsed: Vec<_> = vec![];
        for part in s.split_whitespace() {
            // receiver software version: vX.Y.Z
            // X (major)
            // Y (minor)
            // Z (bugfix)
            if &part[0..1] == "v"
                && part.matches('.').count() == 3
                && status_comment.version.is_none()
            {
                let (first, second) = part
                    .match_indices('.')
                    .nth(2)
                    .map(|(idx, _)| part.split_at(idx))
                    .unwrap();
                status_comment.version = Some(first[1..].into());
                status_comment.platform = Some(second[1..].into());

            // cpu load: CPU:x.x
            // x.x: cpu load as percentage
            } else if part.len() > 4
                && part.starts_with("CPU:")
                && status_comment.cpu_load.is_none()
            {
                if let Ok(cpu_load) = part[4..].parse::<f32>() {
                    status_comment.cpu_load = Decimal::from_f32(cpu_load);
                } else {
                    unparsed.push(part);
                }

            // RAM usage: RAM:x.x/y.yMB
            // x.x: free RAM in MB
            // y.y: total RAM in MB
            } else if part.len() > 6
                && part.starts_with("RAM:")
                && part.ends_with("MB")
                && part.find('/').is_some()
                && status_comment.ram_free.is_none()
            {
                let subpart = &part[4..part.len() - 2];
                let split_point = subpart.find('/').unwrap();
                let (first, second) = subpart.split_at(split_point);
                let ram_free = first.parse::<f32>().ok();
                let ram_total = second[1..].parse::<f32>().ok();
                if ram_free.is_some() && ram_total.is_some() {
                    status_comment.ram_free = ram_free.and_then(Decimal::from_f32);
                    status_comment.ram_total = ram_total.and_then(Decimal::from_f32);
                } else {
                    unparsed.push(part);
                }

            // time synchronisation: NTP:x.xms/y.yppm
            // x.x: NTP offset in [ms]
            // y.y: NTP correction in [ppm]
            } else if part.len() > 6
                && part.starts_with("NTP:")
                && part.find('/').is_some()
                && status_comment.ntp_offset.is_none()
            {
                let subpart = &part[4..part.len() - 3];
                let split_point = subpart.find('/').unwrap();
                let (first, second) = subpart.split_at(split_point);
                let ntp_offset = first[0..first.len() - 2].parse::<f32>().ok();
                let ntp_correction = second[1..].parse::<f32>().ok();
                if ntp_offset.is_some() && ntp_correction.is_some() {
                    status_comment.ntp_offset = ntp_offset.and_then(Decimal::from_f32);
                    status_comment.ntp_correction = ntp_correction.and_then(Decimal::from_f32);
                } else {
                    unparsed.push(part);
                }

            // senders count: x/yAcfts[1h]
            // x: visible senders in the last hour
            // y: total senders in the last hour
            } else if part.len() >= 11
                && part.ends_with("Acfts[1h]")
                && part.find('/').is_some()
                && status_comment.visible_senders.is_none()
            {
                let subpart = &part[0..part.len() - 9];
                let split_point = subpart.find('/').unwrap();
                let (first, second) = subpart.split_at(split_point);
                let visible_senders = first.parse::<u16>().ok();
                let senders = second[1..].parse::<u16>().ok();
                if visible_senders.is_some() && senders.is_some() {
                    status_comment.visible_senders = visible_senders;
                    status_comment.senders = senders;
                } else {
                    unparsed.push(part);
                }

            // latency: Lat:x.xs
            // x.x: latency in [s]
            } else if part.len() > 5
                && part.starts_with("Lat:")
                && part.ends_with("s")
                && status_comment.latency.is_none()
            {
                let latency = part[4..part.len() - 1].parse::<f32>().ok();
                if latency.is_some() {
                    status_comment.latency = latency.and_then(Decimal::from_f32);
                } else {
                    unparsed.push(part);
                }

            // radio frequency informations start with "RF:"
            } else if part.len() >= 11
                && part.starts_with("RF:")
                && status_comment.rf_correction_manual.is_none()
            {
                let values = extract_values(part);
                // short RF format: RF:+x.x/y.yppm/+z.zdB
                // x.x: manual correction in [ppm]
                // y.y: automatic correction in [ppm]
                // z.z: background noise in [dB]
                if values.len() == 3 {
                    let rf_correction_manual = values[0].parse::<i16>().ok();
                    let rf_correction_automatic = values[1].parse::<f32>().ok();
                    let noise = values[2].parse::<f32>().ok();

                    if rf_correction_manual.is_some()
                        && rf_correction_automatic.is_some()
                        && noise.is_some()
                    {
                        status_comment.rf_correction_manual = rf_correction_manual;
                        status_comment.rf_correction_automatic =
                            rf_correction_automatic.and_then(Decimal::from_f32);
                        status_comment.noise = noise.and_then(Decimal::from_f32)
                    } else {
                        unparsed.push(part);
                        continue;
                    }
                // medium RF format: RF:+x.x/y.yppm/+z.zdB/+a.adB@10km[b]
                // a.a: sender signal quality [dB]
                // b: number of messages
                } else if values.len() == 6 {
                    let rf_correction_manual = values[0].parse::<i16>().ok();
                    let rf_correction_automatic = values[1].parse::<f32>().ok();
                    let noise = values[2].parse::<f32>().ok();
                    let senders_signal_quality = values[3].parse::<f32>().ok();
                    let senders_messages = values[5].parse::<u32>().ok();
                    if rf_correction_manual.is_some()
                        && rf_correction_automatic.is_some()
                        && noise.is_some()
                        && senders_signal_quality.is_some()
                        && senders_messages.is_some()
                    {
                        status_comment.rf_correction_manual = rf_correction_manual;
                        status_comment.rf_correction_automatic =
                            rf_correction_automatic.and_then(Decimal::from_f32);
                        status_comment.noise = noise.and_then(Decimal::from_f32);
                        status_comment.senders_signal_quality =
                            senders_signal_quality.and_then(Decimal::from_f32);
                        status_comment.senders_messages = senders_messages;
                    } else {
                        unparsed.push(part);
                        continue;
                    }
                // long RF format: RF:+x.x/y.yppm/+z.zdB/+a.adB@10km[b]/+c.cdB@10km[d/e]
                // c.c: good senders signal quality [dB]
                // d: number of good senders
                // e: number of good and bad senders
                } else if values.len() == 10 {
                    let rf_correction_manual = values[0].parse::<i16>().ok();
                    let rf_correction_automatic = values[1].parse::<f32>().ok();
                    let noise = values[2].parse::<f32>().ok();
                    let senders_signal_quality = values[3].parse::<f32>().ok();
                    let senders_messages = values[5].parse::<u32>().ok();
                    let good_senders_signal_quality = values[6].parse::<f32>().ok();
                    let good_senders = values[8].parse::<u16>().ok();
                    let good_and_bad_senders = values[9].parse::<u16>().ok();
                    if rf_correction_manual.is_some()
                        && rf_correction_automatic.is_some()
                        && noise.is_some()
                        && senders_signal_quality.is_some()
                        && senders_messages.is_some()
                        && good_senders_signal_quality.is_some()
                        && good_senders.is_some()
                        && good_and_bad_senders.is_some()
                    {
                        status_comment.rf_correction_manual = rf_correction_manual;
                        status_comment.rf_correction_automatic =
                            rf_correction_automatic.and_then(Decimal::from_f32);
                        status_comment.noise = noise.and_then(Decimal::from_f32);
                        status_comment.senders_signal_quality =
                            senders_signal_quality.and_then(Decimal::from_f32);
                        status_comment.senders_messages = senders_messages;
                        status_comment.good_senders_signal_quality =
                            good_senders_signal_quality.and_then(Decimal::from_f32);
                        status_comment.good_senders = good_senders;
                        status_comment.good_and_bad_senders = good_and_bad_senders;
                    } else {
                        unparsed.push(part);
                        continue;
                    }
                } else {
                    unparsed.push(part);
                    continue;
                }
            } else if let Some((value, unit)) = split_value_unit(part) {
                // cpu temperature: +x.xC
                // x.x: cpu temperature in [°C]
                if unit == "C" && status_comment.cpu_temperature.is_none() {
                    status_comment.cpu_temperature =
                        value.parse::<f32>().ok().and_then(Decimal::from_f32);
                // voltage: +x.xV
                // x.x: voltage in [V]
                } else if unit == "V" && status_comment.voltage.is_none() {
                    status_comment.voltage = value.parse::<f32>().ok().and_then(Decimal::from_f32);
                // currency: +x.xA
                // x.x: currency in [A]
                } else if unit == "A" && status_comment.amperage.is_none() {
                    status_comment.amperage = value.parse::<f32>().ok().and_then(Decimal::from_f32);
                } else {
                    unparsed.push(part);
                }
            } else {
                unparsed.push(part);
            }
        }
        status_comment.unparsed = if !unparsed.is_empty() {
            Some(unparsed.join(" "))
        } else {
            None
        };

        Ok(status_comment)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sdr() {
        let result = "v0.2.7.RPI-GPU CPU:0.7 RAM:770.2/968.2MB NTP:1.8ms/-3.3ppm +55.7C 7/8Acfts[1h] RF:+54-1.1ppm/-0.16dB/+7.1dB@10km[19481]/+16.8dB@10km[7/13]".parse::<StatusComment>().unwrap();
        assert_eq!(
            result,
            StatusComment {
                version: Some("0.2.7".into()),
                platform: Some("RPI-GPU".into()),
                cpu_load: Decimal::from_f32(0.7),
                ram_free: Decimal::from_f32(770.2),
                ram_total: Decimal::from_f32(968.2),
                ntp_offset: Decimal::from_f32(1.8),
                ntp_correction: Decimal::from_f32(-3.3),
                voltage: None,
                amperage: None,
                cpu_temperature: Decimal::from_f32(55.7),
                visible_senders: Some(7),
                senders: Some(8),
                rf_correction_manual: Some(54),
                rf_correction_automatic: Decimal::from_f32(-1.1),
                noise: Decimal::from_f32(-0.16),
                senders_signal_quality: Decimal::from_f32(7.1),
                senders_messages: Some(19481),
                good_senders_signal_quality: Decimal::from_f32(16.8),
                good_senders: Some(7),
                good_and_bad_senders: Some(13),
                ..Default::default()
            }
        );
    }

    #[test]
    fn test_sdr_different_order() {
        let result = "NTP:1.8ms/-3.3ppm +55.7C CPU:0.7 RAM:770.2/968.2MB 7/8Acfts[1h] RF:+54-1.1ppm/-0.16dB/+7.1dB@10km[19481]/+16.8dB@10km[7/13] v0.2.7.RPI-GPU".parse::<StatusComment>().unwrap();
        assert_eq!(
            result,
            StatusComment {
                version: Some("0.2.7".into()),
                platform: Some("RPI-GPU".into()),
                cpu_load: Decimal::from_f32(0.7),
                ram_free: Decimal::from_f32(770.2),
                ram_total: Decimal::from_f32(968.2),
                ntp_offset: Decimal::from_f32(1.8),
                ntp_correction: Decimal::from_f32(-3.3),
                voltage: None,
                amperage: None,
                cpu_temperature: Decimal::from_f32(55.7),
                visible_senders: Some(7),
                senders: Some(8),
                rf_correction_manual: Some(54),
                rf_correction_automatic: Decimal::from_f32(-1.1),
                noise: Decimal::from_f32(-0.16),
                senders_signal_quality: Decimal::from_f32(7.1),
                senders_messages: Some(19481),
                good_senders_signal_quality: Decimal::from_f32(16.8),
                good_senders: Some(7),
                good_and_bad_senders: Some(13),
                ..Default::default()
            }
        );
    }

    #[test]
    fn test_rf_3() {
        let result = "RF:+29+0.0ppm/+35.22dB".parse::<StatusComment>().unwrap();
        assert_eq!(
            result,
            StatusComment {
                rf_correction_manual: Some(29),
                rf_correction_automatic: Decimal::from_f32(0.0),
                noise: Decimal::from_f32(35.22),
                ..Default::default()
            }
        )
    }

    #[test]
    fn test_rf_6() {
        let result = "RF:+41+56.0ppm/-1.87dB/+0.1dB@10km[1928]"
            .parse::<StatusComment>()
            .unwrap();
        assert_eq!(
            result,
            StatusComment {
                rf_correction_manual: Some(41),
                rf_correction_automatic: Decimal::from_f32(56.0),
                noise: Decimal::from_f32(-1.87),
                senders_signal_quality: Decimal::from_f32(0.1),
                senders_messages: Some(1928),
                ..Default::default()
            }
        )
    }

    #[test]
    fn test_rf_10() {
        let result = "RF:+54-1.1ppm/-0.16dB/+7.1dB@10km[19481]/+16.8dB@10km[7/13]"
            .parse::<StatusComment>()
            .unwrap();
        assert_eq!(
            result,
            StatusComment {
                rf_correction_manual: Some(54),
                rf_correction_automatic: Decimal::from_f32(-1.1),
                noise: Decimal::from_f32(-0.16),
                senders_signal_quality: Decimal::from_f32(7.1),
                senders_messages: Some(19481),
                good_senders_signal_quality: Decimal::from_f32(16.8),
                good_senders: Some(7),
                good_and_bad_senders: Some(13),
                ..Default::default()
            }
        )
    }
}
