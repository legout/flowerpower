# Material UI: Layout Components (`Box`, `Container`, `Grid`, `Stack`)

Structuring page and component layouts using MUI's layout components.

## Core Concept

MUI provides several components specifically designed for handling layout, spacing, and responsiveness, leveraging CSS Flexbox and Grid under the hood.

**Key Layout Components:**

*   **`<Box>`:**
    *   The most basic layout primitive. Renders a `<div>` by default but can be changed using the `component` prop.
    *   Primarily used as a wrapper component to apply styling via the `sx` prop, leveraging the MUI System's shorthand properties (spacing, palette, etc.).
    *   Can be used to quickly implement Flexbox or Grid containers via the `sx` prop (`display: 'flex'`, `display: 'grid'`).
*   **`<Container>`:**
    *   Centers your content horizontally.
    *   Provides a responsive fixed width that changes at different breakpoints (`sm`, `md`, `lg`, `xl`).
    *   Use `maxWidth` prop to control the maximum width (e.g., `maxWidth="lg"`). Set `fixed` prop to use fixed widths matching breakpoints. Set `disableGutters` to remove padding.
*   **`<Grid>`:**
    *   Implements a responsive layout grid system based on a 12-column structure, similar to Bootstrap but using CSS Flexbox.
    *   Requires a `<Grid container>` parent and `<Grid item>` children.
    *   **Container Props:** `spacing` (gap between items, uses `theme.spacing`), `direction` (`row`, `column`), `justifyContent`, `alignItems`.
    *   **Item Props:** Define column spans for different breakpoints (`xs`, `sm`, `md`, `lg`, `xl`). Values are 1-12 (e.g., `xs={12}` for full width on extra-small, `md={6}` for half width on medium+). Use `item` prop on children.
*   **`<Stack>`:**
    *   Manages layout of immediate children along the vertical or horizontal axis with optional spacing and dividers. Uses CSS Flexbox.
    *   **Props:** `direction` (`column` (default), `row`), `spacing` (gap between items, uses `theme.spacing`), `divider` (React node to render between items), `useFlexGap` (uses flexbox `gap` property, recommended).

## Examples

**1. `<Box>` for Styling & Basic Flexbox:**

```jsx
import React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

function BoxDemo() {
  return (
    <Box
      sx={{
        display: 'flex', // Enable flexbox
        justifyContent: 'space-around', // Space items horizontally
        alignItems: 'center', // Center items vertically
        p: 2, // Padding
        border: '1px dashed grey',
        bgcolor: 'lightblue', // Background color shorthand
      }}
    >
      <Button variant="contained">Item 1</Button>
      <Box component="span" sx={{ fontStyle: 'italic' }}>Item 2 (Span)</Box>
      <Button variant="outlined">Item 3</Button>
    </Box>
  );
}
```

**2. `<Container>` for Centering Content:**

```jsx
import React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

function ContainerDemo() {
  return (
    // Content will be centered with max width based on 'lg' breakpoint
    <Container maxWidth="lg">
      <Box sx={{ bgcolor: '#cfe8fc', height: '50vh', p: 2 }}>
        <Typography variant="h4">Centered Content Area</Typography>
        <Typography>
          This content is inside an MUI Container. It centers horizontally and
          has a max-width that adjusts based on the screen size (up to 'lg' here).
        </Typography>
      </Box>
    </Container>
  );
}
```

**3. `<Grid>` for Responsive Layout:**

```jsx
import React from 'react';
import Grid from '@mui/material/Grid'; // Or Unstable_Grid2 for v5+ improvements
import Paper from '@mui/material/Paper';
import { styled } from '@mui/material/styles';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: theme.palette.text.secondary,
}));

function GridDemo() {
  return (
    <Box sx={{ flexGrow: 1, p: 2 }}>
      {/* Grid container with spacing between items */}
      <Grid container spacing={2}>
        {/* Item takes full width on xs, half on sm, one third on md */}
        <Grid item xs={12} sm={6} md={4}>
          <Item>xs=12 sm=6 md=4</Item>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Item>xs=12 sm=6 md=4</Item>
        </Grid>
        <Grid item xs={6} sm={6} md={4}> {/* Takes half width on xs */}
          <Item>xs=6 sm=6 md=4</Item>
        </Grid>
        <Grid item xs={6} sm={12} md={8}> {/* Takes half on xs, full on sm, two thirds on md */}
          <Item>xs=6 sm=12 md=8</Item>
        </Grid>
      </Grid>
    </Box>
  );
}
```
*Note: MUI v5 introduced `Grid2` (`@mui/material/Unstable_Grid2`) which offers more flexibility and potentially better performance. Check documentation.*

**4. `<Stack>` for Linear Layouts:**

```jsx
import React from 'react';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';

function StackDemo() {
  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Stack
        direction="row" // Layout items horizontally
        spacing={2} // Space between items (theme.spacing(2))
        divider={<Divider orientation="vertical" flexItem />} // Vertical divider
        justifyContent="center"
        useFlexGap // Recommended for modern browsers
      >
        <Button variant="outlined">Item 1</Button>
        <Button variant="outlined">Item 2</Button>
        <Button variant="outlined">Item 3</Button>
      </Stack>

      <Stack direction="column" spacing={1} sx={{ mt: 4 }}> {/* Vertical stack */}
        <Paper sx={{ p: 1 }}>Item A</Paper>
        <Paper sx={{ p: 1 }}>Item B</Paper>
        <Paper sx={{ p: 1 }}>Item C</Paper>
      </Stack>
    </Box>
  );
}
```

Choose the appropriate layout component based on your needs: `Box` for simple wrappers and `sx` styling, `Container` for centering page content, `Grid` for complex responsive column layouts, and `Stack` for linear (row or column) arrangements with spacing.

*(Refer to the official MUI documentation for Box, Container, Grid, and Stack.)*