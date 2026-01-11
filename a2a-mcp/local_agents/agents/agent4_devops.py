"""
DevOps Agent - Agent 4 for Scenario 1
======================================
This agent is responsible for DevOps operations including incident management,
service restarts, transaction rollbacks, resource redeployments, and quota management.

Capabilities:
- Analyzes log files for issues
- Performs corrective actions (restart, rollback, redeploy, quota increase)
- Receives requests from Coordinator Agent
- Returns DevOps results via A2A communication

Role: DevOps Automation & Incident Response
"""

import os
import asyncio
from typing import Any, Dict, List
from utils import create_openaichat_client
from dotenv import load_dotenv
import json
from datetime import datetime
from pathlib import Path
import shutil
import textwrap

# Load environment variables
load_dotenv()


class DevOpsAgent:
    """Agent focused on DevOps operations and incident management."""

    def __init__(self):
        """Initialize the DevOps Agent."""
        self.agent_id = "devops-agent"
        self.name = "DevOps Agent"
        self.role = "DevOps Automation & Incident Response"

        # Initialize OpenAI client
        self.client = create_openaichat_client()

        self.deployment_name = "gpt-4o"

        # Agent instructions
        self.system_instructions = """
        You are a DevOps Agent specializing in incident management and operational tasks.
        
        Your responsibilities:
        1. Analyze log files for issues and anomalies
        2. Recommend and execute corrective actions
        3. Perform service restarts, rollbacks, and redeployments
        4. Manage quota increases when needed
        5. Escalate issues when automated resolution is not possible
        
        Available Operations:
        - analyze_logs: Analyze log files for issues
        - restart_service: Restart a named service
        - rollback_transaction: Rollback failed transactions
        - redeploy_resource: Redeploy a named resource
        - increase_quota: Increase system quota
        - escalate_issue: Escalate unresolvable issues
        
        Available Actions based on log analysis:
        - Restart service {service_name}
        - Rollback transaction
        - Redeploy resource {resource_name}
        - Increase quota
        - Escalate issue
        - No action needed
        
        Communication Protocol:
        - You receive requests via A2A messages from the Coordinator
        - You analyze issues and take corrective actions
        - You respond with structured operation results
        - Include action taken and outcome in responses
        
        Be proactive and efficient in incident resolution.
        """

        # Log file paths
        self.script_dir = Path(__file__).parent
        self.log_path = self.script_dir / "logs"

        print(f"✅ {self.name} initialized (ID: {self.agent_id})")
        print(f"   Role: {self.role}")

    def setup_log_files(self) -> str:
        """
        Set up log files by copying from sample_logs directory.

        Returns:
            Path to the logs directory
        """
        src_path = self.script_dir / "sample_logs"
        if src_path.exists():
            shutil.copytree(src_path, self.log_path, dirs_exist_ok=True)
            print(f"   📁 Log files set up in: {self.log_path}")
        return str(self.log_path)

    async def process_devops_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a DevOps request from the Coordinator Agent.

        Args:
            request: Dictionary containing DevOps request details
                - operation: Type of operation (e.g., "analyze_logs", "restart_service")
                - parameters: Operation parameters
                - context: Additional context

        Returns:
            Dictionary containing operation results
        """
        operation = request.get("operation", "unknown")
        parameters = request.get("parameters", {})

        print(f"\n🔧 {self.name} received DevOps request:")
        print(f"   Operation: {operation}")
        print(f"   Parameters: {parameters}")

        try:
            result = await self._execute_operation(operation, parameters)

            return {
                "agent_id": self.agent_id,
                "status": "success",
                "operation": operation,
                "results": result,
                "metadata": {
                    "source": "DevOps MCP Tools",
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            print(f"❌ Error processing DevOps request: {e}")
            return {
                "agent_id": self.agent_id,
                "status": "error",
                "operation": operation,
                "error": str(e)
            }

    async def _execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a DevOps operation.

        Args:
            operation: Operation to execute
            parameters: Operation parameters

        Returns:
            Operation result
        """
        print(f"   🔧 Executing DevOps operation: {operation}...")

        if operation == "analyze_logs":
            return await self._analyze_logs(parameters)

        elif operation == "restart_service":
            return self._restart_service(
                service_name=parameters.get("service_name", ""),
                logfile=parameters.get("logfile", "")
            )

        elif operation == "rollback_transaction":
            return self._rollback_transaction(
                logfile=parameters.get("logfile", "")
            )

        elif operation == "redeploy_resource":
            return self._redeploy_resource(
                resource_name=parameters.get("resource_name", ""),
                logfile=parameters.get("logfile", "")
            )

        elif operation == "increase_quota":
            return self._increase_quota(
                logfile=parameters.get("logfile", "")
            )

        elif operation == "escalate_issue":
            return self._escalate_issue(
                logfile=parameters.get("logfile", ""),
                reason=parameters.get("reason", "Unable to resolve automatically")
            )

        elif operation == "process_log_file":
            return await self._process_log_file(parameters)

        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _analyze_logs(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze log files for issues and recommend actions.

        Args:
            parameters: Parameters including logfile path or directory

        Returns:
            Analysis results with recommendations
        """
        logfile = parameters.get("logfile", "")
        directory = parameters.get("directory", str(self.log_path))

        results = []

        if logfile:
            # Analyze specific log file
            analysis = await self._analyze_single_log(logfile)
            results.append(analysis)
        else:
            # Analyze all log files in directory
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        analysis = await self._analyze_single_log(filepath)
                        results.append(analysis)

        return {
            "analyzed_files": len(results),
            "analyses": results,
            "summary": self._summarize_analyses(results)
        }

    async def _analyze_single_log(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a single log file for issues.

        Args:
            filepath: Path to the log file

        Returns:
            Analysis result with recommended action
        """
        print(f"   📄 Analyzing log file: {filepath}")

        try:
            log_content = self._read_log_file(filepath)

            # Analyze log content for issues
            recommendation = self._determine_action(log_content, filepath)

            return {
                "filepath": filepath,
                "status": "analyzed",
                "recommendation": recommendation,
                "log_preview": log_content[:500] if len(log_content) > 500 else log_content
            }

        except Exception as e:
            return {
                "filepath": filepath,
                "status": "error",
                "error": str(e)
            }

    def _determine_action(self, log_content: str, filepath: str) -> Dict[str, Any]:
        """
        Determine the appropriate action based on log content.

        Args:
            log_content: Content of the log file
            filepath: Path to the log file

        Returns:
            Recommended action details
        """
        log_lower = log_content.lower()

        # Check for service failures
        if "service failure" in log_lower or "multiple failures" in log_lower:
            # Extract service name if present
            service_name = "unknown-service"
            # Look for common service name patterns like "ServiceName:" in logs
            import re
            service_match = re.search(r'(\w+Service):', log_content)
            if service_match:
                service_name = service_match.group(1)
            elif "service" in log_lower:
                # Fallback: simple extraction logic
                parts = log_content.split("service")
                if len(parts) > 1:
                    service_name = parts[1].split()[0].strip(".:,")

            return {
                "action": "restart_service",
                "service_name": service_name,
                "reason": "Multiple service failures detected",
                "logfile": filepath
            }

        # Check for transaction failures
        elif "transaction failure" in log_lower or "transaction error" in log_lower:
            return {
                "action": "rollback_transaction",
                "reason": "Transaction failure detected",
                "logfile": filepath
            }

        # Check for deployment failures
        elif "deployment failure" in log_lower or "resource failure" in log_lower:
            resource_name = "unknown-resource"
            # Look for quoted resource names like 'resource-name' or "resource-name"
            import re
            resource_match = re.search(r"resource ['\"]([^'\"]+)['\"]", log_content, re.IGNORECASE)
            if resource_match:
                resource_name = resource_match.group(1)
            elif "resource" in log_lower:
                parts = log_content.split("resource")
                if len(parts) > 1:
                    resource_name = parts[1].split()[0].strip(".:,'\"")

            return {
                "action": "redeploy_resource",
                "resource_name": resource_name,
                "reason": "Resource deployment failure detected",
                "logfile": filepath
            }

        # Check for quota issues
        elif "quota exceeded" in log_lower or "rate limit" in log_lower or "high request volume" in log_lower:
            return {
                "action": "increase_quota",
                "reason": "Quota/rate limit exceeded",
                "logfile": filepath
            }

        # Check if issue already resolved
        elif "resolved" in log_lower or "successfully" in log_lower:
            return {
                "action": "no_action_needed",
                "reason": "Issue already resolved or no issues found",
                "logfile": filepath
            }

        # Escalate unknown issues
        else:
            return {
                "action": "escalate_issue",
                "reason": "Unknown issue type - requires manual review",
                "logfile": filepath
            }

    def _summarize_analyses(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Create a summary of all log analyses.

        Args:
            analyses: List of analysis results

        Returns:
            Summary string
        """
        if not analyses:
            return "No log files analyzed"

        action_counts = {}
        for analysis in analyses:
            if "recommendation" in analysis:
                action = analysis["recommendation"].get("action", "unknown")
                action_counts[action] = action_counts.get(action, 0) + 1

        summary_parts = [f"{count} {action.replace('_', ' ')}" for action, count in action_counts.items()]
        return f"Analyzed {len(analyses)} log files: " + ", ".join(summary_parts)

    async def _process_log_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a log file by analyzing and taking appropriate action.

        Args:
            parameters: Parameters including logfile path

        Returns:
            Processing result including action taken
        """
        logfile = parameters.get("logfile", "")

        # Analyze the log
        analysis = await self._analyze_single_log(logfile)

        if analysis.get("status") != "analyzed":
            return analysis

        recommendation = analysis.get("recommendation", {})
        action = recommendation.get("action", "no_action_needed")

        # Execute the recommended action
        if action == "restart_service":
            result = self._restart_service(
                service_name=recommendation.get("service_name", "unknown"),
                logfile=logfile
            )
        elif action == "rollback_transaction":
            result = self._rollback_transaction(logfile=logfile)
        elif action == "redeploy_resource":
            result = self._redeploy_resource(
                resource_name=recommendation.get("resource_name", "unknown"),
                logfile=logfile
            )
        elif action == "increase_quota":
            result = self._increase_quota(logfile=logfile)
        elif action == "escalate_issue":
            result = self._escalate_issue(
                logfile=logfile,
                reason=recommendation.get("reason", "")
            )
        else:
            result = {"action": "no_action_needed", "message": "No issues detected"}

        return {
            "logfile": logfile,
            "analysis": analysis,
            "action_taken": result
        }

    # ==================== DevOps Tool Functions ====================

    def _append_to_log_file(self, filepath: str, content: str) -> None:
        """Append content to a log file."""
        with open(filepath, 'a', encoding='utf-8') as file:
            file.write('\n' + textwrap.dedent(content).strip())

    def _read_log_file(self, filepath: str) -> str:
        """Read content from a log file."""
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()

    def _restart_service(self, service_name: str = "", logfile: str = "") -> Dict[str, Any]:
        """
        Restart a named service.

        Args:
            service_name: Name of the service to restart
            logfile: Path to log file for recording action

        Returns:
            Result of the operation
        """
        print(f"   🔄 Restarting service: {service_name}")

        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAgent: Multiple failures detected in {service_name}. Restarting service.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   {service_name}: Restart initiated.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   {service_name}: Service restarted successfully.",
        ]

        if logfile:
            log_message = "\n".join(log_entries)
            self._append_to_log_file(logfile, log_message)

        print(f"   ✅ Service {service_name} restarted successfully")

        return {
            "action": "restart_service",
            "service_name": service_name,
            "message": f"Service {service_name} restarted successfully.",
            "log_updated": bool(logfile)
        }

    def _rollback_transaction(self, logfile: str = "") -> Dict[str, Any]:
        """
        Rollback a failed transaction.

        Args:
            logfile: Path to log file for recording action

        Returns:
            Result of the operation
        """
        print(f"   🔙 Rolling back transaction")

        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAgent: Transaction failure detected. Rolling back transaction batch.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   TransactionProcessor: Rolling back transaction batch.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   Transaction rollback completed successfully.",
        ]

        if logfile:
            log_message = "\n".join(log_entries)
            self._append_to_log_file(logfile, log_message)

        print(f"   ✅ Transaction rolled back successfully")

        return {
            "action": "rollback_transaction",
            "message": "Transaction rolled back successfully.",
            "log_updated": bool(logfile)
        }

    def _redeploy_resource(self, resource_name: str = "", logfile: str = "") -> Dict[str, Any]:
        """
        Redeploy a named resource.

        Args:
            resource_name: Name of the resource to redeploy
            logfile: Path to log file for recording action

        Returns:
            Result of the operation
        """
        print(f"   🚀 Redeploying resource: {resource_name}")

        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAgent: Resource deployment failure detected in '{resource_name}'. Redeploying resource.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   DeploymentManager: Redeployment request submitted.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   DeploymentManager: Service successfully redeployed, resource '{resource_name}' created successfully.",
        ]

        if logfile:
            log_message = "\n".join(log_entries)
            self._append_to_log_file(logfile, log_message)

        print(f"   ✅ Resource '{resource_name}' redeployed successfully")

        return {
            "action": "redeploy_resource",
            "resource_name": resource_name,
            "message": f"Resource '{resource_name}' redeployed successfully.",
            "log_updated": bool(logfile)
        }

    def _increase_quota(self, logfile: str = "") -> Dict[str, Any]:
        """
        Increase system quota.

        Args:
            logfile: Path to log file for recording action

        Returns:
            Result of the operation
        """
        print(f"   📈 Increasing quota")

        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAgent: High request volume detected. Increasing quota.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   APIManager: Quota increase request submitted.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO   APIManager: Quota successfully increased to 150% of previous limit.",
        ]

        if logfile:
            log_message = "\n".join(log_entries)
            self._append_to_log_file(logfile, log_message)

        print(f"   ✅ Quota increased successfully")

        return {
            "action": "increase_quota",
            "message": "Quota successfully increased to 150% of previous limit.",
            "log_updated": bool(logfile)
        }

    def _escalate_issue(self, logfile: str = "", reason: str = "") -> Dict[str, Any]:
        """
        Escalate an issue that cannot be resolved automatically.

        Args:
            logfile: Path to log file for recording action
            reason: Reason for escalation

        Returns:
            Result of the operation
        """
        print(f"   ⚠️  Escalating issue: {reason}")

        log_entries = [
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAgent: Cannot resolve issue.",
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT  DevopsAgent: Requesting escalation. Reason: {reason}",
        ]
        
        if logfile:
            log_message = "\n".join(log_entries)
            self._append_to_log_file(logfile, log_message)

        print(f"   ⚠️  Issue escalated")

        return {
            "action": "escalate_issue",
            "reason": reason,
            "message": "Submitted escalation request.",
            "log_updated": bool(logfile)
        }

    # ==================== A2A Communication ====================

    async def send_to_coordinator(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send results back to the Coordinator Agent via A2A.

        Args:
            message: Message to send to coordinator

        Returns:
            Acknowledgment from coordinator
        """
        print(f"\n📤 Sending results to Coordinator Agent...")
        print(f"   Operation: {message.get('operation', 'unknown')}")
        print(f"   Status: {message.get('status', 'unknown')}")

        # A2A message transmission
        return {
            "status": "delivered",
            "recipient": "coordinator-agent",
            "timestamp": datetime.now().isoformat()
        }

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main message handler for incoming A2A messages.

        Args:
            message: Incoming message from another agent

        Returns:
            Response to send back
        """
        message_type = message.get("type", "unknown")
        sender = message.get("sender", "unknown")

        print(f"\n📨 Received message from {sender}")
        print(f"   Type: {message_type}")

        if message_type == "devops_request":
            # Process DevOps request
            result = await self.process_devops_request(message.get("data", {}))
            return result

        elif message_type == "incident_request":
            # Handle incident management request
            result = await self.process_devops_request({
                "operation": "process_log_file",
                "parameters": message.get("data", {})
            })
            return result

        elif message_type == "ping":
            # Health check
            print(f"   ✅ {self.name}: active")
            return {
                "agent_id": self.agent_id,
                "status": "active",
                "type": "pong"
            }

        else:
            return {
                "agent_id": self.agent_id,
                "status": "error",
                "error": f"Unknown message type: {message_type}"
            }


async def main():
    """Main function to run the DevOps Agent."""
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\n" + "=" * 60)
    print("🤖 DevOps Agent (Agent 4) - Starting...")
    print("=" * 60)

    # Initialize agent
    agent = DevOpsAgent()

    # Set up log files
    agent.setup_log_files()

    # Example 1: Analyze logs
    print("\n--- Example 1: Analyze Logs ---")
    analyze_request = {
        "type": "devops_request",
        "sender": "coordinator-agent",
        "data": {
            "operation": "analyze_logs",
            "parameters": {
                "directory": str(agent.log_path)
            }
        }
    }

    response = await agent.handle_message(analyze_request)
    print(f"\n✅ Analysis completed!")
    print(f"   Response: {json.dumps(response, indent=2)}")

    await agent.send_to_coordinator(response)

    # Example 2: Restart service
    print("\n--- Example 2: Restart Service ---")
    restart_request = {
        "type": "devops_request",
        "sender": "coordinator-agent",
        "data": {
            "operation": "restart_service",
            "parameters": {
                "service_name": "payment-service",
                "logfile": ""
            }
        }
    }

    response = await agent.handle_message(restart_request)
    print(f"\n✅ Operation completed!")
    print(f"   Response: {json.dumps(response, indent=2)}")

    await agent.send_to_coordinator(response)

    # Example 3: Process log files from directory
    print("\n--- Example 3: Process Log Files ---")
    log_path = agent.log_path
    if log_path.exists():
        for filename in os.listdir(log_path):
            filepath = str(log_path / filename)
            print(f"\nProcessing: {filename}")

            process_request = {
                "type": "incident_request",
                "sender": "coordinator-agent",
                "data": {
                    "logfile": filepath
                }
            }

            response = await agent.handle_message(process_request)
            print(f"   Action: {response.get('results', {}).get('action_taken', {}).get('action', 'N/A')}")

    print(f"\n✨ {agent.name} demo completed successfully!")


# Start the app
if __name__ == "__main__":
    asyncio.run(main())