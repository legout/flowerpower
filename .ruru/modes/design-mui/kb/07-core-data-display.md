# Material UI: Data Display Components (MUI Core)

Components for displaying information and collections of data.

## Core Concept

MUI Core offers various components to present data clearly and effectively, ranging from simple text and lists to complex tables and cards.

**Key Data Display Components:**

*   **`<Typography>`:** For rendering text content with appropriate Material Design styles (variants like `h1`-`h6`, `body1`, `caption`, etc.).
*   **`<List>` & `<ListItem>`:** For displaying simple lists of items, often with icons or secondary actions.
*   **`<Table>`:** For displaying structured tabular data with headers, rows, and cells. Includes components for pagination and sorting.
*   **`<Card>`:** A container for grouping related content and actions about a single subject.
*   **`<Avatar>`:** Displays an image, icon, or letters representing a user or entity.
*   **`<Badge>`:** Generates a small badge that appears near another element, typically indicating counts or status.
*   **`<Chip>`:** Compact elements representing input, attributes, or actions.
*   **`<Tooltip>`:** Displays informative text when a user hovers over, focuses on, or touches an element.
*   **`<Divider>`:** A thin line to group content in lists and layouts.

**Importing:** Import components from `@mui/material`. Icons often come from `@mui/icons-material`.

## Common Data Display Components

**1. `<Typography>`:**

*   **Props:** `variant` (`h1`-`h6`, `subtitle1`, `subtitle2`, `body1`, `body2`, `caption`, `overline`, `button`), `component` (override root HTML tag), `gutterBottom` (add margin-bottom), `paragraph` (add margin-bottom, renders as `<p>`), `align` (`left`, `center`, `right`, `justify`), `color` (`primary`, `secondary`, `text.primary`, `text.secondary`, `error`, etc.).

```jsx
import Typography from '@mui/material/Typography';

<Typography variant="h4" component="h1" gutterBottom>
  Page Title (h4 style, h1 tag)
</Typography>
<Typography variant="body1" color="text.secondary">
  This is standard body text with secondary color.
</Typography>
```

**2. `<List>` & `<ListItem>`:**

*   `<List>` acts as the container (`<ul>`).
*   `<ListItem>` represents a list item (`<li>`). Can contain `<ListItemButton>`, `<ListItemIcon>`, `<ListItemText>`, `<ListItemAvatar>`, `secondaryAction`.
*   `<ListItemButton>` makes the item interactive (hover/focus states, often used with `component="a"` or routing library links).
*   `<ListItemText>` displays primary and optional secondary text.

```jsx
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/Inbox';
import DraftsIcon from '@mui/icons-material/Drafts';
import Divider from '@mui/material/Divider';

<List>
  <ListItem disablePadding>
    <ListItemButton component="a" href="#inbox">
      <ListItemIcon><InboxIcon /></ListItemIcon>
      <ListItemText primary="Inbox" secondary="Jan 9, 2024" />
    </ListItemButton>
  </ListItem>
  <Divider />
  <ListItem disablePadding>
    <ListItemButton>
      <ListItemIcon><DraftsIcon /></ListItemIcon>
      <ListItemText primary="Drafts" />
    </ListItemButton>
  </ListItem>
</List>
```

**3. `<Table>`:**

*   Uses standard HTML table elements (`<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`) styled by MUI components: `<TableContainer>`, `<Table>`, `<TableHead>`, `<TableBody>`, `<TableRow>`, `<TableCell>`.
*   `<TableContainer>` often wraps the table, potentially using `<Paper>`.
*   `<TableCell>` props: `align` (`left`, `center`, `right`), `padding`, `size`.
*   Often combined with `<TablePagination>` and `<TableSortLabel>`.

```jsx
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

function createData(name, calories, fat, carbs, protein) { /* ... */ }
const rows = [ /* ... array of data objects ... */ ];

<TableContainer component={Paper}>
  <Table sx={{ minWidth: 650 }} aria-label="simple table">
    <TableHead>
      <TableRow>
        <TableCell>Dessert (100g serving)</TableCell>
        <TableCell align="right">Calories</TableCell>
        {/* ... other headers ... */}
      </TableRow>
    </TableHead>
    <TableBody>
      {rows.map((row) => (
        <TableRow key={row.name} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
          <TableCell component="th" scope="row">{row.name}</TableCell>
          <TableCell align="right">{row.calories}</TableCell>
          {/* ... other cells ... */}
        </TableRow>
      ))}
    </TableBody>
  </Table>
</TableContainer>
```

**4. `<Card>`:**

*   Container for related content.
*   Components: `<Card>`, `<CardContent>`, `<CardActions>`, `<CardHeader>`, `<CardMedia>`.

```jsx
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

<Card sx={{ maxWidth: 345 }}>
  <CardMedia component="img" alt="Lizard" height="140" image="/static/images/lizard.jpg" />
  <CardContent>
    <Typography gutterBottom variant="h5" component="div">Lizard</Typography>
    <Typography variant="body2" color="text.secondary">Lizards are reptiles...</Typography>
  </CardContent>
  <CardActions>
    <Button size="small">Share</Button>
    <Button size="small">Learn More</Button>
  </CardActions>
</Card>
```

**5. Other Useful Components:**

*   **`<Avatar>`:** Displays image, icon, or letters. Props: `src`, `alt`, `children`, `sx` (for custom size/color). Often used in Lists or Cards.
*   **`<Badge>`:** Adds a small badge to corners of other elements. Props: `badgeContent`, `color`, `variant` (`dot`, `standard`), `anchorOrigin`.
*   **`<Chip>`:** Compact element for tags, attributes, or actions. Props: `label`, `variant` (`filled`, `outlined`), `color`, `size`, `icon`, `avatar`, `onDelete`, `clickable`.
*   **`<Tooltip>`:** Shows text label on hover/focus. Wrap the target element. Prop: `title`.
*   **`<Divider>`:** Visual separator. Props: `orientation` (`horizontal`, `vertical`), `variant` (`fullWidth`, `inset`, `middle`), `textAlign` (with text).

Choose the component that best represents the structure and nature of the data you need to display. Combine them with layout components for complex arrangements.

*(Refer to the official MUI documentation for Data Display components.)*