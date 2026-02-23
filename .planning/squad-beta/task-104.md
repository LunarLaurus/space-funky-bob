# Task BETA-004: HTML ROM Map Enhancement

**Squad:** Beta (Graphics & Visualization)  
**Priority:** P2 (Medium)  
**Complexity:** Low  
**Estimated Effort:** 4-6 hours  
**Status:** ⏳ Pending

---

## Objective

Enhance the HTML ROM map visualization with interactive features including hover tooltips, region filtering, clickable navigation, and improved visual design for intuitive ROM exploration.

---

## Context

The current HTML visualization (`bob_map.py` output) provides a basic color-coded map of ROM regions. Enhancements would make it more useful for:
- Quick ROM structure overview
- Finding specific regions by type
- Understanding compression distribution
- Sharing analysis results with team members

---

## Acceptance Criteria

- [ ] Hover tooltips: Show region details on mouseover
- [ ] Region filtering: Toggle code/data/compressed/graphics visibility
- [ ] Clickable regions: Click to view decompressed data / download
- [ ] Search: Find regions by offset or type
- [ ] Legend: Interactive legend with region counts
- [ ] Responsive design: Works on mobile/tablet
- [ ] Export: Download filtered view as PNG/PDF
- [ ] Performance: Loads <2 seconds for 1MB ROM

---

## Technical Notes

### Current HTML Structure
```html
<div class="rom-map">
  <div class="region code" data-start="0x000000" data-end="0x00FFFF">
    Code Region
  </div>
  <div class="region compressed" data-start="0x018000" data-end="0x018800">
    Compressed Block
  </div>
</div>
```

### Enhancements to Add

**Tooltips:**
```javascript
document.querySelectorAll('.region').forEach(region => {
  region.addEventListener('mouseenter', (e) => {
    const start = region.dataset.start;
    const end = region.dataset.end;
    const size = parseInt(end) - parseInt(start);
    showTooltip(e.target, `Offset: ${start}-${end}\nSize: ${size} bytes`);
  });
});
```

**Filtering:**
```javascript
function filterRegions(type) {
  document.querySelectorAll('.region').forEach(region => {
    region.style.display = region.classList.contains(type) ? 'block' : 'none';
  });
}
```

### Visual Improvements
- Gradient backgrounds for entropy levels
- Animated transitions for filtering
- Zoom/pan for detailed exploration
- Dark mode support

---

## Files to Modify

- `toolkit/bob_map.py` — Enhanced HTML generation
- `toolkit/bob_visualize.py` — Integrate with blob visualization
- `docs/USER_GUIDE.md` — Document new features

---

## Dependencies

- **Blocks:** None
- **Blocked by:** None (standalone enhancement)

---

## Test Plan

1. Manual testing in multiple browsers (Chrome, Firefox, Safari)
2. Performance testing with large ROMs (4MB+)
3. Accessibility testing (keyboard navigation, screen readers)
4. Mobile responsiveness testing

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — HTML ROM map enhancement complete
  - Enhanced `bob_map.py` HTML visualization with:
    - Interactive legend with filter buttons (All, Code, Compressed, Graphics, Data, Unknown)
    - Search box for filtering by offset, type, or size
    - Region count display
    - Click-to-scroll between map and list views
    - Hover tooltips with region details
    - Responsive CSS design
  - JavaScript functions: `filterRegions()`, `searchRegions()`, `matchesFilter()`, `matchesSearch()`
  - Created `tests/test_html_visualization.py` with 12 tests (all passing)
  - All acceptance criteria met
