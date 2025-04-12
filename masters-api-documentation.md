# Masters.com Scores API Documentation

## Overview

The Masters.com scores API provides comprehensive real-time data about the Masters golf tournament. This document outlines the structure, endpoints, data formats, and common use cases for this API.

**Base URL:** `https://www.masters.com/en_US/scores/feeds/[YEAR]/scores.json`

Replace `[YEAR]` with the current tournament year (e.g., 2025).

## API Response Structure

The API returns a JSON object with the following high-level structure:

```json
{
  "fileEpoch": "1744473843",
  "data": {
    "currentRound": "0010",
    "wallClockTime": "12:03:41 2025-04-12",
    "statusRound": "FFPNN",
    "yardages": { /* hole yardages */ },
    "pars": { /* hole pars */ },
    "player": [ /* array of player objects */ ]
  }
}
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `fileEpoch` | Unix timestamp of data update | `"1744473843"` |
| `currentRound` | Current tournament round code | `"0010"` (Round 3) |
| `wallClockTime` | Human-readable timestamp | `"12:03:41 2025-04-12"` |
| `statusRound` | Tournament status codes | `"FFPNN"` |

### Course Information

#### Yardages

```json
"yardages": {
  "round1": [445,585,350,240,495,180,450,570,460,495,520,155,545,440,550,170,440,465],
  "round2": [445,585,350,240,495,180,450,570,460,495,520,155,545,440,550,170,440,465],
  "round3": [445,585,350,240,495,180,450,570,460,495,520,155,545,440,550,170,440,465],
  "round4": []
}
```

#### Pars

```json
"pars": {
  "round1": [4,5,4,3,4,3,4,5,4,4,4,3,5,4,5,3,4,4],
  "round2": [4,5,4,3,4,3,4,5,4,4,4,3,5,4,5,3,4,4],
  "round3": [4,5,4,3,4,3,4,5,4,4,4,3,5,4,5,3,4,4],
  "round4": []
}
```

## Player Object

Each player in the tournament has a comprehensive object with the following structure:

```json
{
  "id": "22405",
  "display_name": "ROSE",
  "display_name2": "Rose",
  "first_name": "Justin",
  "last_name": "Rose",
  "full_name": "Justin Rose",
  "countryName": "England",
  "countryCode": "ENG",
  "live": "",
  "video": false,
  "pos": "1",
  "image": true,
  "amateur": false,
  "past": false,
  "firsttimer": false,
  "status": "N",
  "newStatus": "F2",
  "active": false,
  "us": false,
  "intl": true,
  "teetime": "2:40 PM",
  "epoch": 1744483200,
  "tee_order": "52",
  "sort_order": "1|1|1|",
  "start": "SAAA",
  "group": "27",
  "today": "",
  "thru": "",
  "groupHistory": "23|7|27|",
  "thruHistory": "18|18||",
  "lastHoleWithShot": "2|18",
  "holeProgress": 4,
  "topar": "-8",
  "total": "136",
  "totalUnderPar": "true",
  "movement": "0",
  "last_highlight": "2025_r2_22405_18_4",
  "round1": { /* round data */ },
  "round2": { /* round data */ },
  "round3": { /* round data */ },
  "round4": { /* round data */ }
}
```

### Key Player Fields

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique player identifier | `"22405"` |
| `display_name` | Last name in uppercase | `"ROSE"` |
| `display_name2` | Last name in title case | `"Rose"` |
| `full_name` | Complete player name | `"Justin Rose"` |
| `countryName` | Country of representation | `"England"` |
| `countryCode` | ISO country code | `"ENG"` |
| `pos` | Current position | `"1"` or `"T3"` (tied) |
| `amateur` | Amateur status flag | `false` |
| `past` | Past champion flag | `false` |
| `firsttimer` | First tournament flag | `false` |
| `status` | Player status code | `"N"`, `"A"`, `"C"` (cut) |
| `newStatus` | Detailed status code | `"F2"`, `"A3"` |
| `active` | Currently playing flag | `false` |
| `teetime` | Scheduled tee time | `"2:40 PM"` |
| `group` | Playing group number | `"27"` |
| `today` | Today's score | `"-2"` |
| `thru` | Current hole | `"9"` |
| `topar` | Total score relative to par | `"-8"` |
| `total` | Total strokes | `"136"` |
| `totalUnderPar` | Under par flag | `"true"` |
| `movement` | Position change | `"0"`, `"+2"`, `"-3"` |

### Round Data Structure

Each player has round-specific data for all four tournament rounds:

```json
"round1": {
  "prior": null,
  "fantasy": -7,
  "total": 65,
  "roundStatus": "Finished",
  "teetime": "12:00 PM",
  "scores": [3,4,3,3,4,3,4,4,3,3,4,3,5,4,4,2,4,5]
}
```

| Field | Description | Example |
|-------|-------------|---------|
| `prior` | Cumulative score before this round | `-7` or `null` |
| `fantasy` | Fantasy points for the round | `-7` |
| `total` | Total strokes for the round | `65` |
| `roundStatus` | Status of the round | `"Finished"`, `"Playing"`, `"Pre"` |
| `teetime` | Scheduled tee time | `"12:00 PM"` |
| `scores` | Array of hole-by-hole scores | `[3,4,3,3,4,3,4,4,3,3,4,3,5,4,4,2,4,5]` |

## Status Codes

### Player Status (`status`)

| Code | Description |
|------|-------------|
| `N` | Normal status |
| `A` | Active (currently playing) |
| `C` | Cut (missed cut) |

### Detailed Status (`newStatus`)

| Code | Description |
|------|-------------|
| `F2` | Finished round 2 |
| `A3` | Active in round 3 |
| `C` | Cut after round 2 |

## Common Code Examples

### Fetching Tournament Data

```javascript
async function getMastersData() {
  const response = await fetch('https://www.masters.com/en_US/scores/feeds/2025/scores.json');
  const data = await response.json();
  return data;
}
```

### Getting Current Leaderboard

```javascript
function getLeaderboard(data) {
  return data.data.player
    .filter(player => player.status !== 'C')  // Filter out cut players
    .sort((a, b) => {
      // Sort by position (handling tied positions)
      const posA = parseInt(a.pos.replace('T', ''));
      const posB = parseInt(b.pos.replace('T', ''));
      return posA - posB;
    });
}
```

### Finding a Specific Player

```javascript
function findPlayerByName(data, name) {
  const lowerName = name.toLowerCase();
  return data.data.player.find(player => 
    player.full_name.toLowerCase().includes(lowerName)
  );
}
```

### Calculating Round Averages

```javascript
function calculateRoundAverage(data, roundNum) {
  const playersWithCompleteRound = data.data.player.filter(
    player => player[`round${roundNum}`]?.roundStatus === "Finished"
  );
  
  const totals = playersWithCompleteRound.map(
    player => player[`round${roundNum}`].total
  );
  
  return totals.reduce((sum, total) => sum + total, 0) / totals.length;
}
```

### Analyzing Hole Difficulty

```javascript
function getHoleDifficulty(data, roundNum) {
  const difficulties = [];
  
  // For each hole (18 holes)
  for (let hole = 0; hole < 18; hole++) {
    const holeScores = data.data.player
      .filter(player => 
        player[`round${roundNum}`]?.scores && 
        player[`round${roundNum}`].scores[hole] !== null
      )
      .map(player => player[`round${roundNum}`].scores[hole]);
    
    const par = data.data.pars[`round${roundNum}`][hole];
    const avgScore = holeScores.reduce((sum, score) => sum + score, 0) / holeScores.length;
    const relativeToPar = avgScore - par;
    
    difficulties.push({
      hole: hole + 1,
      par,
      avgScore,
      relativeToPar
    });
  }
  
  // Sort by difficulty (highest relative to par first)
  return difficulties.sort((a, b) => b.relativeToPar - a.relativeToPar);
}
```

## Notes and Limitations

1. **Data Refresh Rate**: The API typically updates every few minutes during tournament play.

2. **Access Restrictions**: The API may have rate limits or referrer restrictions.

3. **Status Codes**: Some status codes may change or have additional meanings during special circumstances.

4. **Null Values**: Be prepared to handle null or missing values, especially for upcoming rounds.

5. **Round Numbering**: Rounds are typically numbered as:
   - `"round1"`: First round
   - `"round2"`: Second round
   - `"round3"`: Third round
   - `"round4"`: Final round

## Best Practices

1. **Cache Responses**: To reduce API load, consider caching responses and refreshing at appropriate intervals.

2. **Error Handling**: Implement robust error handling for network issues or unexpected data formats.

3. **Responsive Updates**: For live leaderboards, implement polling with appropriate intervals (e.g., 60 seconds).

4. **Data Validation**: Always validate received data before processing to handle unexpected format changes.

5. **Respect API Limitations**: Follow any documented rate limits and terms of service.
