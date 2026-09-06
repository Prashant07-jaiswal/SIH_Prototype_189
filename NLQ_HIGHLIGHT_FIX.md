# NLQ Node Highlighting Fix

## Problem
When you entered "vikram" in the Natural Language Query (NLQ) bar, the backend correctly returned matching entities and their connections, but **the graph nodes were NOT highlighted visually**. Only the text result appeared in the NLQ result panel.

## Root Cause
1. **QueryBar.jsx** was not passing matched entity IDs to the highlight callback
2. **GraphCanvas.jsx** had `onHighlightPath={null}`, so highlighting was completely disabled
3. The state for tracking NLQ-triggered highlights didn't exist in GraphCanvas

## Solution Implemented

### 1. Updated `QueryBar.jsx`
- Modified `handleQuery()` to extract matched entity IDs from the backend response
- Now passes both `nodeIds` and optional `path` data to the `onHighlightPath` callback:
  ```javascript
  if (onHighlightPath) {
    onHighlightPath({
      nodeIds: highlightedIds,
      path: response.data.path
    });
  }
  ```

### 2. Updated `GraphCanvas.jsx`
- Added state: `const [highlightedNodeIds, setHighlightedNodeIds] = useState([])`
- Created `handleHighlightPath()` function to receive and store highlighted node IDs from QueryBar
- Created `handleSearchChange()` to clear highlights when user clears the search
- Updated the node formatting logic to check **both** search highlights and NLQ highlights
- Changed QueryBar reference from `onHighlightPath={null}` to `onHighlightPath={handleHighlightPath}`

### 3. Updated `main.py` Backend
- Modified `/api/query` endpoint to include `"matches": matches` in the response
- Now returns the full list of matched entity IDs so frontend knows exactly which nodes to highlight

## How It Works Now

**Step-by-step flow:**
1. User types "vikram" in NLQ bar and clicks "Ask"
2. Frontend sends query to `/api/query` endpoint
3. Backend finds all matching entities (e.g., `Vikram Sharma`) and their connected neighbors
4. Backend returns response with `matches` array containing entity IDs
5. QueryBar extracts the IDs and calls `onHighlightPath({nodeIds: [id1, id2, ...]})`
6. GraphCanvas receives the highlighted IDs and updates state
7. On next render, all matched nodes get `isHighlighted = true`
8. Canvas renders these nodes with cyan glow effect:
   ```javascript
   if (node.isHighlighted || (selectedNode && selectedNode.id === node.id)) {
     ctx.fillStyle = 'rgba(0, 240, 255, 0.4)';  // Cyan glow
     ctx.strokeStyle = '#00f0ff';
   }
   ```

## Visual Behavior

**Before Fix:**
- NLQ returns text results only
- Graph nodes remain static
- No visual feedback of which nodes match the query

**After Fix:**
- NLQ returns text results ✅
- All matched nodes glow cyan with a halo effect ✅
- Connected entities are also visible with highlighting ✅
- Highlights clear when search is cleared ✅
- Multiple queries can be run sequentially with fresh highlights ✅

## Testing

To verify the fix works:
1. Click "Run Pipeline & Ingest" to load the graph
2. In the NLQ bar (top-right), type: `vikram`
3. Click "Ask"
4. **Expected:** The result panel shows matching entities + their connections, AND all matched nodes on the graph glow with cyan highlight
5. Type another name like: `ramesh`
6. Click "Ask"
7. **Expected:** Previous highlights clear, new nodes glow

## Files Modified
- ✅ `frontend/src/components/QueryBar.jsx` — Extract and pass matched IDs
- ✅ `frontend/src/components/GraphCanvas.jsx` — Receive, store, and render highlights
- ✅ `backend/main.py` — Include `matches` array in query response
