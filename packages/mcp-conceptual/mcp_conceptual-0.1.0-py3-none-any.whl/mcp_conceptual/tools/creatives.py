"""MCP tools for creatives endpoints."""

from typing import List, Optional

from mcp.server.models import Tool
from mcp.types import TextContent

from ..client import ConceptualAPIClient, ConceptualAPIError


async def get_meta_creative_performance(
    start_date: str,
    end_date: str,
    platform: str = "all",
    status: str = "all",
    limit: int = 100,
    offset: int = 0,
    include_images: bool = True,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get Meta creative performance data from Conceptual API.
    
    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_meta_creative_performance(
                start_date=start_date,
                end_date=end_date,
                platform=platform,
                status=status,
                limit=limit,
                offset=offset,
                include_images=include_images,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )
            
            # Format response for display
            result = []
            result.append(f"Meta Creative Performance ({response.meta.pagination.returned_records} of {response.meta.pagination.total_records} records)")
            result.append(f"Period: {response.meta.period.start_date} to {response.meta.period.end_date}")
            result.append(f"Customer: {response.meta.customer.name}")
            result.append(f"Platform: {response.meta.platform}")
            result.append("")
            
            for creative in response.data:
                result.append(f"Creative: {creative.name} (ID: {creative.id})")
                result.append(f"  Status: {creative.status.display} ({creative.status.color})")
                result.append(f"  Campaign: {creative.campaign.name}")
                result.append(f"  Ad Set: {creative.ad_set.name}")
                result.append(f"  Platform: {creative.platform}")
                
                # Creative assets
                assets = creative.creative_assets
                if assets.headline:
                    result.append(f"  Headline: {assets.headline}")
                if assets.primary_text:
                    result.append(f"  Primary Text: {assets.primary_text[:100]}{'...' if len(assets.primary_text) > 100 else ''}")
                if assets.call_to_action:
                    result.append(f"  CTA: {assets.call_to_action}")
                if assets.creative_type:
                    result.append(f"  Type: {assets.creative_type}")
                if include_images and assets.image_url:
                    result.append(f"  Image: {assets.image_url}")
                
                # Performance metrics
                perf = creative.performance
                result.append(f"  Spend: {perf.spend.formatted}")
                result.append(f"  Impressions: {perf.impressions:,}")
                result.append(f"  Clicks: {perf.clicks:,}")
                result.append(f"  Reach: {perf.reach:,}")
                result.append(f"  Frequency: {perf.frequency:.2f}")
                
                # Detailed metrics
                metrics = perf.metrics
                result.append(f"  CPM: {metrics.cpm.formatted}")
                result.append(f"  CPC: {metrics.cpc.formatted}")
                result.append(f"  CTR: {metrics.ctr.formatted}")
                result.append(f"  Conversion Rate: {metrics.conversion_rate.formatted}")
                result.append(f"  Cost/Conversion: {metrics.cost_per_conversion.formatted}")
                
                # Conversions
                if perf.conversions.total > 0:
                    result.append(f"  Total Conversions: {perf.conversions.total}")
                    if perf.conversions.breakdown:
                        result.append("  Conversion Breakdown:")
                        for conv in perf.conversions.breakdown:
                            result.append(f"    {conv.get('type', 'Unknown')}: {conv.get('count', 0)}")
                
                # Actions available
                actions = creative.actions
                available_actions = []
                if actions.can_pause:
                    available_actions.append("pause")
                if actions.can_activate:
                    available_actions.append("activate")
                if actions.can_edit:
                    available_actions.append("edit")
                if available_actions:
                    result.append(f"  Available Actions: {', '.join(available_actions)}")
                
                result.append("")
            
            return [TextContent(type="text", text="\n".join(result))]
            
    except ConceptualAPIError as e:
        error_msg = f"API Error: {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "Meta" in e.message:
            error_msg += "\nCustomer may not have Meta advertising configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_google_creative_performance(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get Google Ads creative performance data from Conceptual API.
    
    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_google_creative_performance(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )
            
            # Format response for display
            result = []
            result.append(f"Google Creative Performance ({response.meta.pagination.returned_records} of {response.meta.pagination.total_records} records)")
            result.append(f"Period: {response.meta.period.start_date} to {response.meta.period.end_date}")
            result.append(f"Customer: {response.meta.customer.name}")
            result.append("")
            
            for creative in response.data:
                result.append(f"Creative: {creative.name} (ID: {creative.id})")
                result.append(f"  Status: {creative.status.display}")
                result.append(f"  Campaign: {creative.campaign.name}")
                result.append(f"  Platform: {creative.platform}")
                
                # Performance metrics
                perf = creative.performance
                result.append(f"  Spend: {perf.spend.formatted}")
                result.append(f"  Impressions: {perf.impressions:,}")
                result.append(f"  Clicks: {perf.clicks:,}")
                
                # Detailed metrics
                metrics = perf.metrics
                result.append(f"  CPM: {metrics.cpm.formatted}")
                result.append(f"  CPC: {metrics.cpc.formatted}")
                result.append(f"  CTR: {metrics.ctr.formatted}")
                result.append(f"  Conversion Rate: {metrics.conversion_rate.formatted}")
                
                # Conversions
                if perf.conversions.total > 0:
                    result.append(f"  Total Conversions: {perf.conversions.total}")
                
                result.append("")
            
            return [TextContent(type="text", text="\n".join(result))]
            
    except ConceptualAPIError as e:
        error_msg = f"API Error: {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "Google" in e.message:
            error_msg += "\nCustomer may not have Google Ads configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_creative_status(creative_id: str) -> List[TextContent]:
    """Get creative status from Conceptual API."""
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_creative_status(creative_id)
            
            result = []
            result.append(f"Creative Status")
            result.append(f"ID: {response.data.creative_id}")
            result.append(f"Status: {response.data.status}")
            if response.data.last_updated:
                result.append(f"Last Updated: {response.data.last_updated}")
            
            return [TextContent(type="text", text="\n".join(result))]
            
    except ConceptualAPIError as e:
        error_msg = f"API Error: {e.message}"
        if e.status_code == 404:
            error_msg = f"Creative with ID '{creative_id}' not found."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def update_creative_status(creative_id: str, status: str) -> List[TextContent]:
    """Update creative status in Conceptual API.
    
    Rate limit: 10 requests per minute
    Requires Meta OAuth permissions for the customer account.
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.update_creative_status(creative_id, status)
            
            result = []
            result.append(f"Creative Status Updated")
            result.append(f"ID: {response.data.creative_id}")
            result.append(f"Previous Status: {response.data.previous_status}")
            result.append(f"New Status: {response.data.new_status}")
            result.append(f"Updated At: {response.data.updated_at}")
            
            return [TextContent(type="text", text="\n".join(result))]
            
    except ConceptualAPIError as e:
        error_msg = f"API Error: {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Status updates allow 10 requests per minute."
        elif e.status_code == 400:
            error_msg += "\nCheck that the status value is valid (ACTIVE/PAUSED) and customer has proper configuration."
        elif e.status_code == 503:
            error_msg += "\nMeta API issues. Please try again later."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool definitions
CREATIVE_TOOLS = [
    Tool(
        name="get_meta_creative_performance",
        description="""Get Meta (Facebook/Instagram) creative performance data.
        
        Rate limit: 30 requests per minute
        Includes creative assets, performance metrics, and optimization insights.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - platform: meta, google, or all (default: all)
        - status: active, paused, or all (default: all)
        - limit: Max records to return (1-500, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - include_images: Include creative image URLs (default: true)
        - sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        - sort_direction: asc or desc (default: desc)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format"
                },
                "platform": {
                    "type": "string",
                    "enum": ["meta", "google", "all"],
                    "default": "all",
                    "description": "Platform filter"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "paused", "all"],
                    "default": "all",
                    "description": "Filter by creative status"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "default": 100,
                    "description": "Maximum number of records to return"
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip for pagination"
                },
                "include_images": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include creative image URLs in response"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["spend", "impressions", "clicks", "conversions", "cpm", "cpc", "ctr", "conversion_rate"],
                    "description": "Field to sort results by"
                },
                "sort_direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "Sort direction"
                }
            },
            "required": ["start_date", "end_date"]
        }
    ),
    Tool(
        name="get_google_creative_performance",
        description="""Get Google Ads creative (ad assets) performance data.
        
        Rate limit: 30 requests per minute
        Includes asset-level performance metrics and optimization insights.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - limit: Max records to return (1-500, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        - sort_direction: asc or desc (default: desc)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "default": 100,
                    "description": "Maximum number of records to return"
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip for pagination"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["spend", "impressions", "clicks", "conversions", "cpm", "cpc", "ctr", "conversion_rate"],
                    "description": "Field to sort results by"
                },
                "sort_direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "Sort direction"
                }
            },
            "required": ["start_date", "end_date"]
        }
    ),
    Tool(
        name="get_creative_status",
        description="""Get the current status of a specific creative/ad.
        
        Parameters:
        - creative_id: Creative/Ad ID""",
        inputSchema={
            "type": "object",
            "properties": {
                "creative_id": {
                    "type": "string",
                    "description": "Creative/Ad ID to check status for"
                }
            },
            "required": ["creative_id"]
        }
    ),
    Tool(
        name="update_creative_status",
        description="""Update the status of a creative/ad (pause or activate).
        
        Rate limit: 10 requests per minute
        Requires Meta OAuth permissions for the customer account.
        
        Parameters:
        - creative_id: Creative/Ad ID
        - status: New status (ACTIVE, PAUSED, active, or paused - case insensitive)""",
        inputSchema={
            "type": "object",
            "properties": {
                "creative_id": {
                    "type": "string",
                    "description": "Creative/Ad ID to update"
                },
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "PAUSED", "active", "paused"],
                    "description": "New status for the creative (case insensitive)"
                }
            },
            "required": ["creative_id", "status"]
        }
    )
]