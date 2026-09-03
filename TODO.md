# STS2 Run Analyser

## Phase 1 - Foundation
- [x] Create project
- [x] Setup Git
- [x] Setup GitHub
- [x] Create GUI window
- [x] Browse for run directory
- [x] Discover .run files

## Phase 2 - Run Browser
- [x] Convert GUI to grid layout
- [x] Add results frame
- [x] Add run table (Treeview)
- [x] Parse run metadata
- [x] Populate run table
- [x] Sort by date descending
- [x] Select run
- [x] Run details panel

## Phase 3 - Filtering
- [x] Date filter
- [x] Character filter
- [x] Ascension filter
- [x] Win/Loss filter
- [x] Game mode filters
- [x] Game version filter
- [x] Custom date range
- [x] Clear filters

## Phase 4 - Dashboard
- [ ] Overall statistics
- [ ] Character statistics
- [ ] Ascension statistics
- [ ] Recent performance
- [ ] Longest streak
- [ ] Fastest victory

## Phase 5 - Analysis

### Run Analysis
- [ ] Run outcome statistics
- [x] Floor reached analysis
- [ ] Death analysis

### Relic Analysis
- [x] Parse relic acquisitions
- [x] Record relic acquisition source
- [x] Record relic acquisition act / floor / act-floor
- [x] Neow's bonus relic - pick rate
- [x] Neow's bonus relic - win rate
- [x] General relic acquisition statistics
- [x] General relic analysis GUI
- [ ] Relic acquisition analysis by source
- [ ] Relic acquisition timing analysis
- [ ] Relic encounter-performance analysis
- [ ] Relic performance against specific elites
- [ ] Relic performance against specific bosses
- [ ] Relic performance by encounter type

### Card Analysis
- [ ] Card reward analysis
- [ ] Card pick rate
- [ ] Card win rate
- [ ] Card skip rate
- [ ] Card analysis by character
- [ ] Card analysis by ascension
- [ ] Card acquisition act / floor / act-floor tracking
- [ ] Card encounter-performance analysis
- [ ] Card performance against specific elites
- [ ] Card performance against specific bosses
- [ ] Card → run observed win-rate analysis
- [ ] Card → run analysis by acquisition timing
- [ ] Card → run analysis by character / ascension / act
- [ ] Card → card correlation analysis
- [ ] Advanced card analysis

### Event Analysis
- [ ] Event decision analysis
- [ ] Event option pick rate
- [ ] Event option win rate
- [ ] Event analysis by character
- [ ] Event analysis by ascension
- [ ] Complex event relic analysis

### Combat / Death Analysis
- [x] Encounter parsing
- [x] Encounter location tracking
- [x] Combat performance statistics
- [x] Damage taken analysis
- [x] Turns per fight analysis
- [x] Elite encounter analysis
- [x] Boss encounter analysis
- [x] Most common cause of death
- [x] Deaths by enemy
- [ ] Deaths by enemy type
- [ ] Death floor analysis
- [ ] Encounter-level analysis framework
- [ ] Encounter filtering by type
- [ ] Encounter filtering by specific elite/boss
- [ ] Separate encounter outcome from overall run outcome
- [ ] Encounter performance analysis by item presence

### Encounter Analysis
- [ ] Reusable encounter-level statistics
- [ ] Normal / elite / boss encounter filtering
- [ ] Specific encounter filtering
- [ ] Determine item presence at encounter from act / floor / act-floor
- [ ] Encounter win/loss statistics
- [ ] Encounter damage statistics
- [ ] Encounter turn statistics
- [ ] Encounter performance by relic
- [ ] Encounter performance by card

### Path Analysis
- [ ] Path choice analysis
- [ ] Node type frequency
- [ ] Path choices vs win rate

## Phase 6 - Visualisation

### Quick Plots
- [x] Quick Plot framework
- [x] Win rate - overall
- [x] Win rate - by character
- [x] Win rate - by Ascension
- [x] Win rate - by character and Ascension
- [ ] Win rate over time
- [ ] Automatic plot updates when filters change

### Future plots
- [ ] Character usage
- [ ] Average floor reached
- [ ] Deck size distribution
- [ ] Card pick frequency
- [ ] Relic acquisition frequency
- [ ] Relic acquisition timing
- [ ] Boss relic choices
- [ ] Event outcomes
- [ ] Encounter win rates
- [ ] Item performance against encounters
- [ ] Card win-rate comparison (with card vs without card)
- [ ] Card correlation visualisation

## Phase 7 - Polish
- [ ] Remember last run directory
- [ ] Export filtered runs to CSV
- [ ] Export statistics
- [ ] Dark/light themes
- [ ] Settings
- [ ] Performance improvements
- [ ] Clean up remaining IDE/type warnings
- [ ] Fix remaining analysis-window graphical issues
- [ ] Improve plot presentation/UX

## Testing & Quality
- [x] Statistics tests
- [x] Filtering tests
- [x] Plot tests
- [x] Metadata parser tests
- [x] Encounter parser tests
- [x] Relic parser tests
- [x] Relic analysis tests
- [x] Combat analysis tests
- [ ] Card analysis tests
- [ ] Card correlation tests
- [ ] GUI integration tests
- [ ] Expand edge-case coverage