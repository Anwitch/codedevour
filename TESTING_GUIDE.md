# 🧪 Code Explorer - Manual Testing Guide

## ✅ Test Checklist

### 1. **Server Setup** ✅ DONE
- [x] Server running at http://127.0.0.1:5000
- [x] Code Explorer page accessible at /visualizer
- [x] All static files loaded (CSS, JS)

---

### 2. **Page Loading Test**

**Steps:**
1. Open http://127.0.0.1:5000/ (main page)
2. Click "🔍 Code Explorer" chip in top navigation
3. Verify page loads without errors

**Expected Result:**
- ✅ Page shows "Code Explorer" title
- ✅ Three panels visible: Filters | Graph | Details
- ✅ "📊 Scan Project" button visible
- ✅ "← Back to Main" button visible
- ✅ No console errors

---

### 3. **Scan Project Test**

**Steps:**
1. Click "📊 Scan Project" button
2. Wait for loading overlay (spinner)
3. Check graph appears

**Expected Result:**
- ✅ Loading overlay shows "Scanning project..."
- ✅ After scan: Bubble graph appears with nodes
- ✅ Stats badge updates (e.g., "19 files • 50 functions")
- ✅ "🔄 Refresh" button appears
- ✅ No errors in console

**Check Server Logs:**
```
127.0.0.1 - - [Date] "POST /api/visualizer/scan HTTP/1.1" 200 -
127.0.0.1 - - [Date] "GET /api/visualizer/graph HTTP/1.1" 200 -
127.0.0.1 - - [Date] "GET /api/visualizer/stats HTTP/1.1" 200 -
```

---

### 4. **Graph Interaction Tests**

#### 4.1 **Zoom & Pan**
**Steps:**
1. Scroll mouse wheel up/down over graph
2. Drag canvas (not on nodes)

**Expected Result:**
- ✅ Mouse wheel zoom in/out works
- ✅ Drag canvas pans the view
- ✅ Graph stays within bounds

#### 4.2 **Node Click**
**Steps:**
1. Click any bubble/node in graph

**Expected Result:**
- ✅ Node border becomes crimson (selected state)
- ✅ Details sidebar updates with file info:
  - File path
  - Lines, size, centrality score
  - Functions list
  - Classes list
  - Dependencies (imports, imported by)
- ✅ Other nodes dim slightly (focus effect)

#### 4.3 **Node Hover**
**Steps:**
1. Hover over any node (don't click)

**Expected Result:**
- ✅ Tooltip appears showing file name
- ✅ Node size slightly increases
- ✅ Cursor changes to pointer

#### 4.4 **Drag Node**
**Steps:**
1. Click and drag a node to new position

**Expected Result:**
- ✅ Node moves with mouse
- ✅ Edges (connections) update dynamically
- ✅ Force simulation adjusts other nodes
- ✅ Node stays in new position when released

---

### 5. **Search & Filter Tests**

#### 5.1 **Search**
**Steps:**
1. Type "app" in search input (filter panel)
2. Wait 300ms (debounce)

**Expected Result:**
- ✅ Nodes matching "app" highlight in crimson
- ✅ Non-matching nodes fade out/gray
- ✅ Graph auto-focuses on matches

#### 5.2 **Language Filter**
**Steps:**
1. Select "Python" from language dropdown
2. Click "Apply Filters"

**Expected Result:**
- ✅ Only Python files remain visible
- ✅ Other language files hide
- ✅ Graph re-layouts

#### 5.3 **Size Filter**
**Steps:**
1. Set Min size: 5 KB
2. Set Max size: 50 KB
3. Click "Apply Filters"

**Expected Result:**
- ✅ Only files between 5-50 KB show
- ✅ Smaller/larger files hide
- ✅ Graph re-renders

#### 5.4 **Reset Filters**
**Steps:**
1. Apply some filters
2. Click "Reset" button

**Expected Result:**
- ✅ All filters clear
- ✅ Search input clears
- ✅ All nodes reappear
- ✅ Graph returns to initial state

---

### 6. **Details Sidebar Tests**

#### 6.1 **Function Click**
**Steps:**
1. Click any node to show details
2. Click a function name in sidebar

**Expected Result:**
- ✅ Graph highlights the file containing that function
- ✅ Function's file node gets selected
- ✅ Sidebar updates to show clicked file

#### 6.2 **Dependency Click**
**Steps:**
1. Click any node
2. In "Imports from" section, click an import

**Expected Result:**
- ✅ Graph navigates to imported file
- ✅ Imported file node becomes selected
- ✅ Sidebar updates with imported file details

#### 6.3 **Empty State**
**Steps:**
1. Before scanning, check sidebar

**Expected Result:**
- ✅ Shows "Select a file to view details"
- ✅ Empty state icon visible
- ✅ No errors

---

### 7. **Graph Controls Tests**

#### 7.1 **Reset View**
**Steps:**
1. Zoom/pan around
2. Click 🏠 (home icon) button

**Expected Result:**
- ✅ Graph resets to initial zoom level
- ✅ Graph centers on canvas
- ✅ All nodes visible

#### 7.2 **Export SVG**
**Steps:**
1. Click 💾 (save icon) button

**Expected Result:**
- ✅ Download dialog appears
- ✅ File named "codebase-graph.svg" downloads
- ✅ SVG file opens correctly in browser
- ✅ Graph structure preserved

#### 7.3 **Fullscreen**
**Steps:**
1. Click ⛶ (fullscreen icon) button
2. Click again to exit

**Expected Result:**
- ✅ Graph container goes fullscreen
- ✅ Filters/sidebar still accessible
- ✅ Exit fullscreen works

---

### 8. **Navigation Tests**

#### 8.1 **Back to Main**
**Steps:**
1. Click "← Back to Main" button

**Expected Result:**
- ✅ Returns to main CodeDevour page
- ✅ Shows NamesExtractor/TextExtractor UI
- ✅ No navigation errors

#### 8.2 **Main to Explorer**
**Steps:**
1. From main page, click "🔍 Code Explorer" chip

**Expected Result:**
- ✅ Navigates to /visualizer
- ✅ Previous graph state preserved (if scanned before)
- ✅ Smooth transition

---

### 9. **Error Handling Tests**

#### 9.1 **Empty Project**
**Steps:**
1. Scan empty folder (if possible)

**Expected Result:**
- ✅ Shows error message or empty state
- ✅ No crash
- ✅ User-friendly message

#### 9.2 **Server Down**
**Steps:**
1. Stop Flask server
2. Try to scan project

**Expected Result:**
- ✅ Shows network error message
- ✅ Loading overlay disappears
- ✅ No infinite loading

---

### 10. **Performance Tests**

#### 10.1 **Large Project**
**Steps:**
1. Scan CodeDevour project (~46 Python files)

**Expected Result:**
- ✅ Scan completes in < 10 seconds
- ✅ Graph renders smoothly
- ✅ Zoom/pan stays at 60fps
- ✅ No browser freeze

#### 10.2 **Many Interactions**
**Steps:**
1. Click 20+ different nodes rapidly
2. Search multiple times
3. Apply various filters

**Expected Result:**
- ✅ UI remains responsive
- ✅ No memory leaks
- ✅ Graph updates smoothly
- ✅ No console errors

---

## 📊 Test Results Summary

Fill in during testing:

| Test Category | Status | Notes |
|--------------|--------|-------|
| Page Loading | ⏳ | |
| Scan Project | ⏳ | |
| Zoom & Pan | ⏳ | |
| Node Click | ⏳ | |
| Search | ⏳ | |
| Filters | ⏳ | |
| Details Sidebar | ⏳ | |
| Graph Controls | ⏳ | |
| Navigation | ⏳ | |
| Error Handling | ⏳ | |
| Performance | ⏳ | |

Legend: ✅ Pass | ❌ Fail | ⏳ Pending | ⚠️ Issue

---

## 🐛 Bugs Found

Track issues here:

1. **[BUG-001]** Description...
   - **Steps to reproduce:**
   - **Expected:**
   - **Actual:**
   - **Priority:** High/Medium/Low

---

## 🎯 Final Verdict

- [ ] All critical features working
- [ ] No major bugs
- [ ] Performance acceptable
- [ ] Ready for Week 3

**Overall Status:** ⏳ Testing in Progress

---

## 📝 Next Actions

After testing complete:
1. Fix any bugs found
2. Document improvements needed
3. Update WEEK2_COMPLETE.md with test results
4. Proceed to Week 3 or iterate on Week 2

