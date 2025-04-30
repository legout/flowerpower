# Material UI: Input & Control Components (MUI Core)

Commonly used MUI Core components for user input and actions.

## Core Concept

MUI Core provides a rich set of components for capturing user input, triggering actions, and making selections, all styled according to Material Design.

**Key Component Categories:**

*   **Buttons:** Trigger actions.
*   **Text Fields:** Single-line or multi-line text input.
*   **Selection Controls:** Checkboxes, Radio buttons, Switches.
*   **Select Dropdown:** Choose from a list of options.
*   **Slider:** Select a value from a range.
*   **Autocomplete:** Text field with typeahead/suggestion capabilities.

**Importing:** Import components directly from `@mui/material`.

## Common Input Components

**1. `<Button>`:**

*   **Variants:** `contained` (default), `outlined`, `text`.
*   **Props:** `color` (`primary`, `secondary`, `error`, etc.), `size` (`small`, `medium`, `large`), `disabled`, `startIcon`, `endIcon`, `href` (renders as `<a>`), `onClick`.

```jsx
import Button from '@mui/material/Button';
import SendIcon from '@mui/icons-material/Send';

<Button variant="contained" color="primary" endIcon={<SendIcon />}>
  Send
</Button>
```

**2. `<TextField>`:**

*   **Purpose:** Versatile text input. Can be single-line, multi-line, number input, etc.
*   **Variants:** `outlined` (default), `filled`, `standard`.
*   **Props:** `label` (placeholder text that moves), `variant`, `color`, `size`, `type` (`text`, `password`, `number`, `email`, `date`, etc.), `multiline`, `rows`, `maxRows`, `required`, `error` (boolean), `helperText`, `value`, `onChange`, `InputProps` (for start/end adornments), `InputLabelProps`. Often used with form libraries.

```jsx
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import AccountCircle from '@mui/icons-material/AccountCircle';

<TextField
  error={hasError} // Boolean to show error state
  id="username"
  label="Username"
  defaultValue="Default Value"
  helperText={hasError ? "Incorrect entry." : "Enter your username"}
  variant="outlined" // or "filled" or "standard"
  margin="normal" // Adds vertical margin
  required
  fullWidth // Takes full width of container
  InputProps={{
    startAdornment: (
      <InputAdornment position="start">
        <AccountCircle />
      </InputAdornment>
    ),
  }}
/>

<TextField
  id="description"
  label="Description"
  multiline
  rows={4}
  variant="outlined"
/>
```

**3. Selection Controls:**

*   **`<Checkbox>`:**
    *   Props: `checked`, `onChange`, `disabled`, `color`, `size`, `indeterminate`. Often used with `<FormControlLabel>`.
*   **`<Radio>` & `<RadioGroup>`:**
    *   `<Radio>` Props: `checked`, `value`, `disabled`, `color`, `size`.
    *   `<RadioGroup>` Props: `value` (controlled value), `onChange`, `row` (display horizontally), `name`. Wrap `<Radio>` components inside `<RadioGroup>` and use `<FormControlLabel>`.
*   **`<Switch>`:**
    *   Props: `checked`, `onChange`, `disabled`, `color`, `size`. Often used with `<FormControlLabel>`.
*   **`<FormControlLabel>`:**
    *   Convenience component to wrap a control (`Checkbox`, `Radio`, `Switch`) with a `label`.
    *   Props: `control` (the control component instance), `label`, `labelPlacement` (`end`, `start`, `top`, `bottom`), `value` (needed for Radio within RadioGroup).

```jsx
import Checkbox from '@mui/material/Checkbox';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';

// Checkbox
<FormControlLabel control={<Checkbox defaultChecked />} label="Agree to terms" />

// Radio Group
<FormControl component="fieldset">
  <FormLabel component="legend">Gender</FormLabel>
  <RadioGroup
    row // Display horizontally
    aria-label="gender"
    name="gender-radio-group"
    value={selectedValue} // Controlled state
    onChange={handleChange}
  >
    <FormControlLabel value="female" control={<Radio />} label="Female" />
    <FormControlLabel value="male" control={<Radio />} label="Male" />
    <FormControlLabel value="other" control={<Radio />} label="Other" />
  </RadioGroup>
</FormControl>

// Switch
<FormControlLabel control={<Switch checked={isChecked} onChange={handleSwitchChange} />} label="Enable Feature" />
```

**4. `<Select>`:**

*   **Purpose:** Dropdown selection.
*   **Components:** `<FormControl>`, `<InputLabel>`, `<Select>`, `<MenuItem>`.
*   **Props (`<Select>`):** `value` (controlled value), `onChange`, `label`, `labelId` (associates with `<InputLabel>`), `multiple` (allow multiple selections), `variant` (`outlined`, `filled`, `standard`).

```jsx
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';

const [age, setAge] = React.useState('');
const handleChange = (event: SelectChangeEvent) => { setAge(event.target.value); };

<FormControl fullWidth margin="normal">
  <InputLabel id="age-select-label">Age</InputLabel>
  <Select
    labelId="age-select-label"
    id="age-select"
    value={age}
    label="Age"
    onChange={handleChange}
  >
    <MenuItem value={10}>Ten</MenuItem>
    <MenuItem value={20}>Twenty</MenuItem>
    <MenuItem value={30}>Thirty</MenuItem>
  </Select>
</FormControl>
```

**5. `<Slider>`:**

*   **Purpose:** Select a value or range from a continuous or discrete set.
*   **Props:** `value`, `onChange`, `min`, `max`, `step`, `marks` (boolean or array for tick marks), `valueLabelDisplay` (`auto`, `on`, `off`), `orientation` (`horizontal`, `vertical`), `disabled`.

```jsx
import Slider from '@mui/material/Slider';
import Box from '@mui/material/Box';

function valuetext(value: number) { return `${value}°C`; }

<Box sx={{ width: 300 }}>
  <Slider
    aria-label="Temperature"
    defaultValue={30}
    getAriaValueText={valuetext}
    valueLabelDisplay="auto"
    step={10}
    marks // Show default marks
    min={10}
    max={110}
  />
</Box>
```

**6. `<Autocomplete>`:**

*   **Purpose:** Combines a text input with a dropdown of suggestions. Can fetch options dynamically.
*   **Props:** `options` (array of available options), `renderInput={(params) => <TextField {...params} label="Movie" />}` (renders the text field), `value`, `onChange`, `inputValue`, `onInputChange`, `getOptionLabel`, `isOptionEqualToValue`, `freeSolo` (allow arbitrary input), `multiple` (select multiple options).

```jsx
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';

const top100Films = [ /* ... array of { label: string, year: number } ... */ ];

<Autocomplete
  disablePortal
  id="combo-box-demo"
  options={top100Films}
  sx={{ width: 300 }}
  renderInput={(params) => <TextField {...params} label="Movie" />}
  // getOptionLabel={(option) => option.label} // Use if options are objects
  // onChange={(event, newValue) => { console.log(newValue); }}
/>
```

These components form the building blocks for most user interactions in MUI applications. Refer to the official documentation for detailed props and advanced usage patterns.

*(Refer to the official MUI documentation for Inputs, Buttons, Selection Controls, etc.)*