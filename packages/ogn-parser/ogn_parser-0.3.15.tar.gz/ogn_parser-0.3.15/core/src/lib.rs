//! [APRS] message parser for [Rust]
//!
//! [APRS]: http://www.aprs.org/
//! [Rust]: https://www.rust-lang.org/
//!
//! # Usage
//!
//! ```rust
//! extern crate ogn_parser;
//!
//! fn main() {
//!     let result = ogn_parser::parse(
//!         r"ICA3D17F2>APRS,qAS,dl4mea:/074849h4821.61N\01224.49E^322/103/A=003054"
//!     );
//!
//!     println!("{:#?}", result);
//!
//!     // Ok(
//!     //     AprsPacket {
//!     //         from: Callsign {
//!     //             call: "ICA3D17F2",
//!     //             ssid: None
//!     //         },
//!     //         to: Callsign {
//!     //             call: "APRS",
//!     //             ssid: None
//!     //         },
//!     //         via: [
//!     //             Callsign {
//!     //                 call: "qAS",
//!     //                 ssid: None
//!     //             },
//!     //             Callsign {
//!     //                 call: "dl4mea",
//!     //                 ssid: None
//!     //             }
//!     //         ],
//!     //         data: Position(
//!     //             AprsPosition {
//!     //                 timestamp: Some(
//!     //                     HHMMSS(
//!     //                         7,
//!     //                         48,
//!     //                         49
//!     //                     )
//!     //                 ),
//!     //                 latitude: 48.360165,
//!     //                 longitude: 12.408166666666666,
//!     //                 comment: "322/103/A=003054"
//!     //             }
//!     //         )
//!     //     }
//!     // )
//! }
//! ```

// `!(-90. ..=90.).contains(&value)` seems worse than `value > 90. || value < -90.`
#![allow(clippy::manual_range_contains)]

extern crate thiserror;

#[cfg(test)]
#[macro_use]
extern crate approx;

mod callsign;
mod comment;
mod error;
mod lonlat;
mod message;
mod packet;
mod position;
mod position_comment;
mod server_comment;
mod server_response;
mod status;
mod status_comment;
mod timestamp;
mod utils;

use std::str::FromStr;

pub use callsign::Callsign;
pub use comment::Comment;
pub use error::{AprsError, EncodeError};
pub use lonlat::{Latitude, Longitude};
pub use message::AprsMessage;
pub use packet::{AprsData, AprsPacket};
pub use position::AprsPosition;
pub use position_comment::{AdditionalPrecision, ID, PositionComment};
pub use server_comment::ServerComment;
pub use server_response::ServerResponse;
pub use status::AprsStatus;
pub use status_comment::StatusComment;
pub use timestamp::Timestamp;

pub fn parse(s: &str) -> Result<AprsPacket, AprsError> {
    AprsPacket::from_str(s)
}
