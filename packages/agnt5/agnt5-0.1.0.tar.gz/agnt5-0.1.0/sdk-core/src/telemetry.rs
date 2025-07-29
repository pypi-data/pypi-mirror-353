use opentelemetry::{global, KeyValue, Context};
use opentelemetry_otlp::{WithExportConfig, Protocol};
use opentelemetry::sdk::{
    trace::{TracerProvider, BatchConfig, Sampler},
    Resource, runtime
};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use std::env;
use crate::error::SdkError;

pub struct SdkTelemetry {
    _resource: Resource,
}

impl SdkTelemetry {
    pub fn init_from_env() -> Result<Self, SdkError> {
        let config = TelemetryConfig::from_env();
        
        let resource = Resource::new(vec![
            KeyValue::new("service.name", config.service_name.clone()),
            KeyValue::new("service.version", config.service_version.clone()),
            KeyValue::new("service.environment", config.environment.clone()),
            KeyValue::new("component", "sdk-core"),
            KeyValue::new("language", "rust"),
        ]);

        Self::setup_otel_providers(&config, resource.clone())?;
        Self::setup_tracing_subscriber()?;
        
        Ok(Self {
            _resource: resource,
        })
    }
    
    fn setup_otel_providers(config: &TelemetryConfig, resource: Resource) 
        -> Result<(), SdkError> {
        
        if !config.enable_tracing {
            return Ok(());
        }
        
        // Setup OTLP trace exporter with simplified approach
        let trace_exporter = opentelemetry_otlp::new_exporter()
            .tonic()
            .with_endpoint(&config.otel_endpoint)
            .with_protocol(Protocol::Grpc);
            
        let _tracer_provider = opentelemetry_otlp::new_pipeline()
            .tracing()
            .with_exporter(trace_exporter)
            .with_trace_config(
                opentelemetry::sdk::trace::Config::default()
                    .with_sampler(Sampler::TraceIdRatioBased(config.sampling_rate))
                    .with_resource(resource.clone())
            )
            .install_batch(runtime::Tokio)
            .map_err(|e| SdkError::TelemetryError(format!("Failed to setup tracer: {}", e)))?;

        Ok(())
    }
    
    fn setup_tracing_subscriber() -> Result<(), SdkError> {
        use tracing_subscriber::{fmt, EnvFilter};
        
        // Setup tracing with file and line number information
        let subscriber = fmt::Subscriber::builder()
            .with_env_filter(EnvFilter::from_default_env())
            .with_target(false)
            .with_file(true)      // Include file names
            .with_line_number(true)  // Include line numbers
            .finish();
            
        tracing::subscriber::set_global_default(subscriber)
            .map_err(|e| SdkError::TelemetryError(format!("Failed to set tracing subscriber: {}", e)))?;
            
        Ok(())
    }
    
    pub fn get_tracer(name: &'static str) -> impl opentelemetry::trace::Tracer {
        global::tracer(name)
    }
    
    pub fn get_meter(name: &'static str) -> opentelemetry::metrics::Meter {
        global::meter(name)
    }
    
    pub async fn shutdown(self) -> Result<(), SdkError> {
        global::shutdown_tracer_provider();
        Ok(())
    }
}

#[derive(Debug, Clone)]
pub struct TelemetryConfig {
    pub service_name: String,
    pub service_version: String,
    pub environment: String,
    pub otel_endpoint: String,
    pub enable_tracing: bool,
    pub enable_metrics: bool,
    pub enable_logging: bool,
    pub sampling_rate: f64,
}

impl TelemetryConfig {
    pub fn from_env() -> Self {
        Self {
            service_name: env::var("AGNT5_SERVICE_NAME").unwrap_or_else(|_| "sdk-core".to_string()),
            service_version: env::var("AGNT5_SERVICE_VERSION").unwrap_or_else(|_| "0.1.0".to_string()),
            environment: env::var("AGNT5_ENV").unwrap_or_else(|_| "development".to_string()),
            otel_endpoint: env::var("AGNT5_OTEL_ENDPOINT").unwrap_or_else(|_| "http://localhost:4317".to_string()),
            enable_tracing: env::var("AGNT5_ENABLE_TRACING").unwrap_or_else(|_| "true".to_string()) == "true",
            enable_metrics: env::var("AGNT5_ENABLE_METRICS").unwrap_or_else(|_| "true".to_string()) == "true",
            enable_logging: env::var("AGNT5_ENABLE_LOGGING").unwrap_or_else(|_| "true".to_string()) == "true",
            sampling_rate: env::var("AGNT5_SAMPLING_RATE")
                .unwrap_or_else(|_| "1.0".to_string())
                .parse()
                .unwrap_or(1.0),
        }
    }
}

// Helper macros for common telemetry operations
#[macro_export]
macro_rules! trace_function {
    ($name:expr, $($key:expr => $value:expr),*) => {
        let tracer = opentelemetry::global::tracer("sdk-core");
        let span = tracer
            .span_builder($name)
            .with_kind(opentelemetry::trace::SpanKind::Internal)
            .with_attributes(vec![
                $(opentelemetry::KeyValue::new($key, $value)),*
            ])
            .start(&tracer);
        let _guard = span.mark_as_active();
    };
}

#[macro_export]
macro_rules! record_metric {
    (counter, $name:expr, $value:expr, $($key:expr => $attr_value:expr),*) => {
        let meter = opentelemetry::global::meter("sdk-core");
        let counter = meter.u64_counter($name).init();
        counter.add($value, &[
            $(opentelemetry::KeyValue::new($key, $attr_value)),*
        ]);
    };
    (histogram, $name:expr, $value:expr, $($key:expr => $attr_value:expr),*) => {
        let meter = opentelemetry::global::meter("sdk-core");
        let histogram = meter.f64_histogram($name).init();
        histogram.record($value, &[
            $(opentelemetry::KeyValue::new($key, $attr_value)),*
        ]);
    };
}

// Initialize global telemetry - should be called once at startup
pub fn init_global_telemetry() -> Result<SdkTelemetry, SdkError> {
    SdkTelemetry::init_from_env()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;

    #[test]
    fn test_telemetry_config_from_env() {
        unsafe {
            env::set_var("AGNT5_SERVICE_NAME", "test-service");
            env::set_var("AGNT5_SERVICE_VERSION", "1.0.0");
            env::set_var("AGNT5_ENV", "test");
            env::set_var("AGNT5_OTEL_ENDPOINT", "http://test:4317");
            env::set_var("AGNT5_SAMPLING_RATE", "0.5");
        }

        let config = TelemetryConfig::from_env();
        
        assert_eq!(config.service_name, "test-service");
        assert_eq!(config.service_version, "1.0.0");
        assert_eq!(config.environment, "test");
        assert_eq!(config.otel_endpoint, "http://test:4317");
        assert_eq!(config.sampling_rate, 0.5);
        assert!(config.enable_tracing);
        assert!(config.enable_metrics);
        assert!(config.enable_logging);
    }

    #[test]
    fn test_telemetry_config_defaults() {
        // Clear environment variables
        unsafe {
            env::remove_var("AGNT5_SERVICE_NAME");
            env::remove_var("AGNT5_SERVICE_VERSION");
            env::remove_var("AGNT5_ENV");
            env::remove_var("AGNT5_OTEL_ENDPOINT");
            env::remove_var("AGNT5_SAMPLING_RATE");
        }

        let config = TelemetryConfig::from_env();
        
        assert_eq!(config.service_name, "sdk-core");
        assert_eq!(config.service_version, "0.1.0");
        assert_eq!(config.environment, "development");
        assert_eq!(config.otel_endpoint, "http://localhost:4317");
        assert_eq!(config.sampling_rate, 1.0);
    }
}