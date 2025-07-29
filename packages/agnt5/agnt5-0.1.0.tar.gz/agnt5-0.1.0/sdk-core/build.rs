use std::env;
use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Get the project root directory (where Cargo.toml is located)
    let cargo_manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    
    // Try multiple potential paths for the proto directory
    let potential_proto_dirs = vec![
        // Standard relative path from sdk-core
        cargo_manifest_dir.join("..").join("..").join("protos").join("proto"),
        // Alternative path if built from different context (like Docker)
        PathBuf::from("/app/protos/proto"),
        // Another alternative path
        cargo_manifest_dir.parent().unwrap().join("protos").join("proto"),
    ];
    
    let proto_dir = potential_proto_dirs
        .iter()
        .find(|dir| dir.exists())
        .cloned()
        .unwrap_or_else(|| {
            eprintln!("Proto directory not found in any of these locations:");
            for dir in &potential_proto_dirs {
                eprintln!("  {:?}", dir);
            }
            eprintln!("CARGO_MANIFEST_DIR: {:?}", cargo_manifest_dir);
            panic!("Proto directory not found");
        });
    
    println!("Using proto directory: {:?}", proto_dir);
    
    // Get paths to the specific proto files that the SDK needs
    let api_v1_dir = proto_dir.join("api").join("v1");
    let common_proto = api_v1_dir.join("common.proto");
    let gateway_proto = api_v1_dir.join("gateway.proto");
    let worker_coordinator_proto = api_v1_dir.join("worker_coordinator.proto");
    
    // Check if the proto files exist
    let proto_files = vec![
        &common_proto,
        &gateway_proto,
        &worker_coordinator_proto,
    ];
    
    for proto_file in &proto_files {
        if !proto_file.exists() {
            panic!("{:?} not found at: {:?}", proto_file.file_name().unwrap(), proto_file);
        }
    }
    
    // Make sure the output directory exists
    let out_dir = cargo_manifest_dir.join("src").join("pb");
    std::fs::create_dir_all(&out_dir)?;
    
    // Compile protocol buffers
    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .out_dir(&out_dir)  // Output generated code to src/pb
        .compile_protos(
            &[
                common_proto.to_str().unwrap(),
                gateway_proto.to_str().unwrap(),
                worker_coordinator_proto.to_str().unwrap(),
            ],
            &[proto_dir.to_str().unwrap()],
        )?;
    
    // Tell Cargo to recompile if the proto files change
    for proto_file in &proto_files {
        println!("cargo:rerun-if-changed={}", proto_file.display());
    }
    println!("cargo:rerun-if-changed={}", proto_dir.display());
    
    Ok(())
}