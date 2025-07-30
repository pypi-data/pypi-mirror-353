"""Command line interface for AgentForce SDK."""

import json
import logging
import sys
import os

import click

from agent_sdk import Agentforce
from agent_sdk.core.auth import BasicAuth
from agent_sdk.exceptions import AgentforceAuthError
from agent_sdk.models import Agent
from agent_sdk.utils.agent_utils import AgentUtils
from .utils.dependent_metadata_utils import (
    validate_dependent_metadata,
    get_metadata_summary,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """AgentForce SDK command line interface.

    Use this CLI to create, deploy, and manage agents on Salesforce.
    """
    pass


@cli.command()
@click.option("--username", "-u", required=True, help="Salesforce username")
@click.option("--password", "-p", required=True, help="Salesforce password")
@click.option("--agent-file", "-f", help="Path to agent JSON file")
@click.option("--agent-name", "-n", help="Name of the agent of the agent json file")
@click.option("--agent-dir", "-d", help="Path to agent directory (for modular files)")
@click.option("--dependent-metadata", help="Path to folder containing custom metadata files to use instead of default classes")
@click.option("--deploy", is_flag=True, help="Deploy the agent to Salesforce")
def create(username, password, agent_file, agent_name, agent_dir, dependent_metadata, deploy):
    """Create an agent from a file or directory."""
    if not agent_file and not agent_dir:
        click.echo("Error: Either --agent-file or --agent-dir must be provided.")
        sys.exit(1)

    if agent_file and agent_dir:
        click.echo("Error: Cannot provide both --agent-file and --agent-dir.")
        sys.exit(1)
    
    if agent_dir and not agent_name:
        click.echo("Error: --agent-name is required when using --agent-dir.")
        sys.exit(1)

    # Validate dependent metadata directory if provided
    metadata_ok_for_deploy = True
    if dependent_metadata:
        if not os.path.exists(dependent_metadata):
            click.echo(f"Error: Dependent metadata directory not found: {dependent_metadata}")
            sys.exit(1)
        if not os.path.isdir(dependent_metadata):
            click.echo(f"Error: Dependent metadata path must be a directory: {dependent_metadata}")
            sys.exit(1)
        
        click.echo(f"Using dependent metadata from: {dependent_metadata}")
        click.echo("Validating dependent metadata...")
        is_valid, validation_errors = validate_dependent_metadata(dependent_metadata)
        
        if not is_valid:
            metadata_ok_for_deploy = False # Mark as not OK if any validation error
            click.echo("⚠️  Dependent metadata validation found issues:")
            for error in validation_errors:
                click.echo(f"  - {error}")
            if deploy:
                click.echo("Error: Dependent metadata validation failed. Deployment aborted.")
                sys.exit(1)
            else:
                click.echo("Continuing to create agent definition (without deployment due to validation issues)...")
        else:
            click.echo("✅ Dependent metadata validation passed")
            
        try:
            summary = get_metadata_summary(dependent_metadata)
            click.echo(f"📦 Metadata Summary:")
            click.echo(f"  - Total files: {summary['total_files']}")
            click.echo(f"  - Has package.xml: {'Yes' if summary['has_package_xml'] else 'No'}")
        except Exception as e:
            logger.debug(f"Could not generate metadata summary: {e}")
            click.echo("  (Could not generate detailed summary)")

    agent = None
    try:
        if agent_file:
            click.echo(f"Creating agent from file: {agent_file}")
            # It's better to let AgentUtils handle file opening and JSON parsing errors
            agent = AgentUtils.create_agent_from_file(agent_file, dependent_metadata_dir=dependent_metadata)
        elif agent_dir:
            click.echo(f"Creating agent from directory: {agent_dir}")
            if not agent_name: # Should be caught earlier, but as a safeguard
                 click.echo("Error: --agent-name is required with --agent-dir for modular agent creation.")
                 sys.exit(1)
            agent = AgentUtils.create_agent_from_modular_files(
                base_dir=agent_dir, agent_name=agent_name, dependent_metadata_dir=dependent_metadata
            )

        if agent:
            click.echo(f"Agent Name: {agent.name}")
            click.echo(f"Agent Type: {agent.agent_type}")
            click.echo(f"Topics: {len(agent.topics) if agent.topics else 0}")

        if deploy:
            if not metadata_ok_for_deploy and dependent_metadata:
                # This check is a bit redundant due to the sys.exit(1) earlier for deploy mode,
                # but kept for clarity if the flow changes.
                click.echo("Error: Cannot deploy due to dependent metadata validation issues.")
                sys.exit(1)
            
            if not agent: # Agent creation failed
                click.echo("Error: Agent definition could not be created. Deployment aborted.")
                sys.exit(1)

            click.echo("Deploying agent to Salesforce...")
            client = Agentforce(auth=BasicAuth(username=username, password=password)) # Initialize client only if deploying
            result = client.create(agent, dependent_metadata_dir=dependent_metadata)
            if result and result.get("success"):
                click.echo(f"Agent deployed successfully: ID - {result.get('agent_id', 'N/A')}")
            else:
                click.echo(f"Agent deployment failed. Result: {result}")
                sys.exit(1)
        elif agent: # If not deploying but agent creation was successful
            click.echo("Agent definition created successfully. To deploy, use the --deploy flag.")

    except FileNotFoundError as e:
        click.echo(f"Error: Agent file/directory not found: {e.filename}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid agent JSON file: {e.msg} (line {e.lineno} col {e.colno})")
        sys.exit(1)
    except AgentforceAuthError as e:
        click.echo(f"Authentication error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")
        logger.debug("Full stack trace:", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option("--username", "-u", required=True, help="Salesforce username")
@click.option("--password", "-p", required=True, help="Salesforce password")
@click.option("--agent-name", "-n", required=True, help="Agent name to chat with")
@click.option("--message", "-m", required=True, help="Message to send to the agent")
@click.option("--session-id", "-s", help="Session ID for continuing a conversation")
def chat(username, password, agent_name, message, session_id):
    """Send a message to an agent."""
    # Initialize the client
    client = Agentforce(auth=BasicAuth(username=username, password=password))

    try:
        # Send message to agent
        click.echo(f"Sending message to agent '{agent_name}': {message}")
        response = client.send_message(
            agent_name=agent_name, user_message=message, session_id=session_id
        )

        # Print response
        click.echo(f"\nAgent response: {response['agent_response']}")
        click.echo(f"Session ID: {response['session_id']}")

    except AgentforceAuthError as e:
        click.echo(f"Authentication error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error sending message: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--username", "-u", required=True, help="Salesforce username")
@click.option("--password", "-p", required=True, help="Salesforce password")
def list_agents(username, password):
    """List all agents in the Salesforce org."""
    # Initialize the client
    client = Agentforce(auth=BasicAuth(username=username, password=password))

    try:
        # List agents
        agents = client.list_agents()

        # Print agent details
        click.echo(f"Found {len(agents)} agents:")
        for agent in agents:
            click.echo(f"- {agent['MasterLabel']} (API Name: {agent['DeveloperName']})")

    except AgentforceAuthError as e:
        click.echo(f"Authentication error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error listing agents: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
