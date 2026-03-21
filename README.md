# User's Edge Browser Tabs Metadata

The `edge_all_open_tabs` object provides important context about the user's browsing session in Microsoft Edge.  
- The tab with `isCurrent=true` is the user's **currently active/viewing tab**.  
- Tabs with `isCurrent=false` are other open tabs in the background.

## Structure

Each tab entry contains:
- **pageTitle**: The title of the web page.
- **pageUrl**: The URL of the web page.
- **tabId**: A unique identifier for the tab.
- **isCurrent**: Boolean flag indicating if this tab is the active tab.

## Example

```json
edge_all_open_tabs = [
  {
    "pageTitle": "Ride Distance Calculator",
    "pageUrl": "http://127.0.0.1/index.html",
    "tabId": 616861364,
    "isCurrent": true
  },
  {
    "pageTitle": "peekay11/eviiDrive: for drivers to price their rides",
    "pageUrl": "https://github.com/peekay11/eviiDrive",
    "tabId": 616861285,
    "isCurrent": false
  },
  {
    "pageTitle": "OSRM API Documentation",
    "pageUrl": "https://project-osrm.org/docs/v5.24.0/api",
    "tabId": 616861353,
    "isCurrent": false
  }
]
