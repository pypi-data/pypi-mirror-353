//! Generated Protocol Buffer types for AGNT5 SDK Core
//! 
//! This module contains all the generated protobuf types used for
//! communication with the AGNT5 runtime platform.

pub mod api_v1 {
    //! API v1 protobuf definitions
    include!("api.v1.rs");
}

pub mod google_api {
    //! Google API protobuf definitions
    include!("google.api.rs");
}

// Re-export commonly used types for convenience
pub use api_v1::*;