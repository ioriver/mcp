# IO River MCP Server

A remote MCP server for the [IO River](https://ioriver.io) multi-CDN platform,
built with Python, FastMCP, and FastAPI.

## Available Tools

### Services

| Tool                              | Description                                  |
| --------------------------------- | -------------------------------------------- |
| `list_services`                   | List all IO River services                   |
| `get_service`                     | Get details of a specific service            |
| `create_service`                  | Create a new service                         |
| `update_service`                  | Update an existing service                   |
| `delete_service`                  | Delete a service                             |
| `list_domains`                    | List domains for a service                   |
| `create_domain`                   | Add a domain to a service                    |
| `update_domain`                   | Update a domain                              |
| `delete_domain`                   | Remove a domain from a service               |
| `list_origins`                    | List origin servers for a service            |
| `create_origin`                   | Add an origin to a service                   |
| `update_origin`                   | Update an origin                             |
| `delete_origin`                   | Remove an origin from a service              |
| `list_service_providers`          | List CDN providers attached to a service     |
| `add_service_provider`            | Attach a CDN provider to a service           |
| `remove_service_provider`         | Detach a CDN provider from a service         |
| `attach_certificate_to_service`   | Attach an SSL certificate to a service       |
| `remove_certificate_from_service` | Remove a certificate from a service          |
| `replace_certificate_in_service`  | Replace a certificate on a service           |
| `list_geo_restrictions`           | List geo restriction rules for a service     |
| `list_log_destinations`           | List log export destinations for a service   |
| `list_protocol_configs`           | List protocol configs (HTTP/2, HTTP/3, IPv6) |
| `list_url_signing_keys`           | List URL signing keys for a service          |

### Behaviors

| Tool              | Description                                |
| ----------------- | ------------------------------------------ |
| `list_behaviors`  | List cache/routing behaviors for a service |
| `get_behavior`    | Get a specific behavior                    |
| `create_behavior` | Create a new behavior with actions         |
| `update_behavior` | Update an existing behavior                |
| `delete_behavior` | Delete a behavior                          |

### Traffic Policies

| Tool                    | Description                       |
| ----------------------- | --------------------------------- |
| `list_traffic_policies` | List CDN traffic routing policies |
| `get_traffic_policy`    | Get a specific traffic policy     |
| `create_traffic_policy` | Create a traffic routing policy   |
| `update_traffic_policy` | Update a traffic routing policy   |
| `delete_traffic_policy` | Delete a traffic policy           |

### Account Providers

| Tool                      | Description                                |
| ------------------------- | ------------------------------------------ |
| `list_account_providers`  | List all CDN providers in the account      |
| `get_account_provider`    | Get details of a specific account provider |
| `create_account_provider` | Add a CDN provider to the account          |
| `update_account_provider` | Update an account provider                 |
| `delete_account_provider` | Remove a CDN provider from the account     |

### Certificates

| Tool                 | Description                 |
| -------------------- | --------------------------- |
| `list_certificates`  | List SSL/TLS certificates   |
| `get_certificate`    | Get a specific certificate  |
| `create_certificate` | Create/upload a certificate |
| `update_certificate` | Update a certificate        |
| `delete_certificate` | Delete a certificate        |

### Monitors (Health & Performance)

| Tool                       | Description                        |
| -------------------------- | ---------------------------------- |
| `list_health_checks`       | List health checks for a service   |
| `get_health_check`         | Get a specific health check        |
| `create_health_check`      | Create a health check              |
| `update_health_check`      | Update a health check              |
| `delete_health_check`      | Delete a health check              |
| `list_performance_checks`  | List performance monitoring checks |
| `get_performance_check`    | Get a specific performance check   |
| `create_performance_check` | Create a performance check         |
| `update_performance_check` | Update a performance check         |
| `delete_performance_check` | Delete a performance check         |

### Cache Purge

| Tool                | Description                            |
| ------------------- | -------------------------------------- |
| `purge_cache`       | Purge cached content by URL            |
| `purge_cache_tags`  | Purge cached content by cache tags     |
| `purge_all`         | Purge all cached content for a service |
| `get_purge_history` | Get purge operation history            |

### Alerts

| Tool                  | Description                              |
| --------------------- | ---------------------------------------- |
| `list_alerts`         | List all configured alerts               |
| `list_alert_channels` | List alert notification channels         |
| `test_alert`          | Trigger a test notification for an alert |

### Traffic Analytics

| Tool                                 | Description                                            |
| ------------------------------------ | ------------------------------------------------------ |
| `get_traffic_analytics_overtime`     | Get traffic metrics (requests/bytes) over time         |
| `get_traffic_analytics_top_stats`    | Get top values per dimension (country, provider, etc.) |
| `get_traffic_analytics_sampled_logs` | Get sampled CDN traffic log entries                    |
| `get_traffic_stats`                  | Get basic traffic statistics for a service             |

### Security Analytics (WAF)

| Tool                             | Description                                              |
| -------------------------------- | -------------------------------------------------------- |
| `get_security_requests_overtime` | Get WAF blocked/allowed request counts over time         |
| `get_security_top_stats`         | Get top WAF request attributes (country, IP, path, etc.) |
| `get_security_sampled_logs`      | Get sampled raw WAF log entries                          |

### Events

| Tool                             | Description                               |
| -------------------------------- | ----------------------------------------- |
| `get_traffic_events_for_service` | Get traffic events for a specific service |
| `get_traffic_events_for_account` | Get traffic events across the account     |

## Using the IO River MCP Server

The server is publicly available at **https://mcp.ioriver.io/mcp**.

You need an IO River API token to authenticate. Your token is passed as a Bearer header and forwarded directly to the IO River API — the server never stores it.

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ioriver": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.ioriver.io/mcp", "--header", "Authorization: Bearer YOUR_IORIVER_API_TOKEN"]
    }
  }
}
```

Config file location:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Cursor / VS Code (GitHub Copilot)

Add to your MCP settings:

```json
{
  "servers": {
    "ioriver": {
      "url": "https://mcp.ioriver.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_IORIVER_API_TOKEN"
      }
    }
  }
}
```

### Direct HTTP (for testing)

```bash
curl -X POST https://mcp.ioriver.io/mcp \
  -H "Authorization: Bearer YOUR_IORIVER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Local Development

```bash
pipenv install
pipenv run python src/main.py
```

Server starts on http://localhost:3000. Use the same `curl` command above substituting `http://localhost:3000/mcp`.

## Example Prompts

- _"List all my IO River services"_
- _"Show traffic policies for service abc123"_
- _"Purge the cache for /images/\* on service abc123"_
- _"Show traffic stats for the last 24 hours on service abc123"_
- _"Which countries had the most traffic in the last day?"_
- _"What traffic was blocked by security in the last 24 hours?"_
- _"Show me the top security threats on service abc123 today"_
- _"Create a behavior to cache /static/\* for 5 minutes"_
- _"Add a Fastly provider to my service abc123 and route 50% of the traffic to it"_
- _"Are there any active alerts?"_
