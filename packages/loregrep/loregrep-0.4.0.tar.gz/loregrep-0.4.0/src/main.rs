// Placeholder main.rs for CLI interface
// Will be implemented in Phase 6

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::PathBuf;
use tokio;

// Use the CLI wrapper for clean access to CLI functionality
use loregrep::cli_main::{CliConfig, CliApp, AnalyzeArgs, QueryArgs, ScanArgs, SearchArgs};

#[derive(Parser)]
#[command(name = "loregrep")]
#[command(about = "Lightweight Code Analysis Tool with AI-powered search")]
#[command(long_about = "Loregrep analyzes codebases using tree-sitter parsing and provides AI-powered natural language search capabilities")]
#[command(version)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,

    /// Working directory for all operations
    #[arg(short, long, global = true, default_value = ".")]
    pub directory: PathBuf,

    /// Enable verbose output
    #[arg(short, long, global = true)]
    pub verbose: bool,

    /// Disable colored output
    #[arg(long, global = true)]
    pub no_color: bool,

    /// Configuration file path
    #[arg(short, long, global = true)]
    pub config: Option<PathBuf>,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Scan a repository for code analysis
    Scan(ScanArgs),
    /// Search for functions, structs, or other code elements
    Search(SearchArgs),
    /// Analyze a specific file
    Analyze(AnalyzeArgs),
    /// Show current configuration
    Config,
    /// Interactive natural language query mode
    Query(QueryArgs),
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    let cli = Cli::parse();

    // Load configuration
    let config = CliConfig::load(cli.config.as_deref())?;

    // Initialize CLI app
    let mut app = CliApp::new(config, cli.verbose, !cli.no_color).await?;

    // Execute command
    match cli.command {
        Commands::Scan(mut args) => {
            // Override path with global directory if not explicitly set
            if args.path == PathBuf::from(".") {
                args.path = cli.directory;
            }
            app.scan(args).await
        },
        Commands::Search(mut args) => {
            // Override path with global directory if not explicitly set
            if args.path == PathBuf::from(".") {
                args.path = cli.directory;
            }
            app.search(args).await
        },
        Commands::Analyze(mut args) => {
            // If analyzing current directory, use global directory
            if args.file == PathBuf::from(".") {
                args.file = cli.directory;
            } else if args.file.is_relative() {
                // If relative path, make it relative to global directory
                args.file = cli.directory.join(args.file);
            }
            app.analyze(args).await
        },
        Commands::Config => app.show_config().await,
        Commands::Query(mut args) => {
            // Override path with global directory if not explicitly set
            if args.path == PathBuf::from(".") {
                args.path = cli.directory;
            }
            app.query(args).await
        },
    }
} 