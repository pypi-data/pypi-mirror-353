"""
MCP server providing pylint functionality
"""

from datetime import datetime, UTC

from mcp.server.fastmcp import FastMCP, Context
from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter

mcp = FastMCP("pylint", dependencies=["pylint"])

async def run_pylint(source_file: str):
    """
    Run pylint against a file
    """
    now = datetime.now(UTC).isoformat()
    log_file = f"/tmp/pylint_report-{now}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        reporter = JSONReporter(f)
        Run([source_file], reporter=reporter, exit=False)
    return log_file

@mcp.tool()
async def lint(filename: str, ctx: Context = None) -> str:
    """
    Check a python file for syntactic errors using pylint.

    Parameters:
        filename (str): The python source file to check.
        ctx (Context, optional): MCP context for logging or progress reporting.

    Returns:
        str: A JSON-serialized object containing any errors reported by pylint
    """
    ctx.info(f"Running pylint on {filename}")
    outfile = await run_pylint(filename)
    content = ""
    with open(outfile, 'r', encoding="utf-8") as file:
        content = file.read()
    return content

def main() -> None:
    """
    Run the mcp server
    """
    mcp.run()
