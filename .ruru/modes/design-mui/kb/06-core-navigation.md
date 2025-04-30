# Material UI: Navigation Components (MUI Core)

Components for implementing navigation patterns like app bars, drawers, menus, and tabs.

## Core Concept

MUI Core provides components to structure application navigation according to Material Design guidelines, supporting responsive patterns and common interactions.

**Key Navigation Components:**

*   **`<AppBar>` & `<Toolbar>`:** For top application bars, often containing titles, navigation icons, and action buttons.
*   **`<Drawer>`:** A sliding panel (usually from the left or right) for navigation menus or supplementary content, common on mobile or dense UIs.
*   **`<Menu>` & `<MenuItem>`:** For temporary dropdown menus triggered by buttons or other elements.
*   **`<BottomNavigation>` & `<BottomNavigationAction>`:** A navigation bar fixed to the bottom, common on mobile.
*   **`<Breadcrumbs>` & `<Link>`:** Shows the user's path within the application hierarchy.
*   **`<Tabs>` & `<Tab>`:** Allows switching between different views or sections within the same context.
*   **`<Link>`:** A styled link component that integrates with the theme's typography and colors.

**Importing:** Import components from `@mui/material`. Icons often come from `@mui/icons-material`.

## Common Navigation Components

**1. `<AppBar>` & `<Toolbar>`:**

*   `<AppBar>` provides the container with Material Design elevation and color.
*   `<Toolbar>` arranges items horizontally within the AppBar, typically handling padding.
*   Use `<IconButton>`, `<Typography>`, `<Button>` inside the `<Toolbar>`.

```jsx
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box'; // Used for flex grow

function MyAppBar() {
  return (
    <AppBar position="static"> {/* Or "fixed", "sticky", etc. */}
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }} // Margin right
        >
          <MenuIcon />
        </IconButton>
        {/* Title takes available space */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          My App
        </Typography>
        <Button color="inherit">Login</Button>
      </Toolbar>
    </AppBar>
  );
}
```

**2. `<Drawer>`:**

*   Controlled component using `open` prop and `onClose` handler.
*   `variant`: `permanent`, `persistent`, `temporary` (most common for responsive sidebars).
*   `anchor`: `left` (default), `right`, `top`, `bottom`.
*   Often contains `<List>` and `<ListItem>` components for navigation links.

```jsx
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import Box from '@mui/material/Box';

function MyDrawer({ open, onClose }) { // Receive state and handler as props
  const DrawerList = (
    <Box sx={{ width: 250 }} role="presentation" onClick={onClose}>
      <List>
        {['Inbox', 'Starred', 'Send email', 'Drafts'].map((text, index) => (
          <ListItem key={text} disablePadding>
            <ListItemButton>
              <ListItemIcon>
                {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
              </ListItemIcon>
              <ListItemText primary={text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      {/* Add Divider, other lists as needed */}
    </Box>
  );

  return (
    <Drawer anchor="left" open={open} onClose={onClose}>
      {DrawerList}
    </Drawer>
  );
}
// Usage typically involves state in parent component to control 'open'
// const [drawerOpen, setDrawerOpen] = React.useState(false);
// <MyAppBar menuButtonClick={() => setDrawerOpen(true)} />
// <MyDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
```

**3. `<Menu>` & `<MenuItem>`:**

*   Controlled component anchored to another element.
*   Use `anchorEl` state to store the element the menu is anchored to.
*   `open` prop controls visibility. `onClose` handles closing.

```jsx
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import React from 'react';

function MyMenu() {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div>
      <Button
        id="basic-button"
        aria-controls={open ? 'basic-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        onClick={handleClick}
      >
        Dashboard
      </Button>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{ 'aria-labelledby': 'basic-button' }}
      >
        <MenuItem onClick={handleClose}>Profile</MenuItem>
        <MenuItem onClick={handleClose}>My account</MenuItem>
        <MenuItem onClick={handleClose}>Logout</MenuItem>
      </Menu>
    </div>
  );
}
```

**4. `<Tabs>` & `<Tab>`:**

*   Manages a set of tabs and their associated content panels.
*   Requires state to control the `value` (index or unique ID) of the currently selected tab.
*   `onChange` handler updates the state.
*   Use `value` and `index` (or unique ID) props on `<Tab>` and corresponding panels.

```jsx
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import React from 'react';

// Helper component for tab panels
function CustomTabPanel(props) { /* ... see MUI docs ... */ }

function MyTabs() {
  const [value, setValue] = React.useState(0);
  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Item One" id="tab-0" aria-controls="panel-0" />
          <Tab label="Item Two" id="tab-1" aria-controls="panel-1" />
        </Tabs>
      </Box>
      <CustomTabPanel value={value} index={0}> {/* Content for Tab 1 */}
        Item One Content
      </CustomTabPanel>
      <CustomTabPanel value={value} index={1}> {/* Content for Tab 2 */}
        Item Two Content
      </CustomTabPanel>
    </Box>
  );
}
```

**5. `<Breadcrumbs>` & `<Link>`:**

*   `<Breadcrumbs>` displays the navigation path.
*   `<Link>` component provides themed links, often used within `<Breadcrumbs>`. Can integrate with routing libraries via `component` prop.

```jsx
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link'; // MUI Link
import Typography from '@mui/material/Typography';
// import { Link as RouterLink } from 'react-router-dom'; // Example router link

function MyBreadcrumbs() {
  return (
    <Breadcrumbs aria-label="breadcrumb">
      <Link underline="hover" color="inherit" href="/"> {/* Or component={RouterLink} to="/"} */}
        MUI
      </Link>
      <Link underline="hover" color="inherit" href="/material-ui/getting-started/installation/">
        Core
      </Link>
      <Typography color="text.primary">Breadcrumbs</Typography>
    </Breadcrumbs>
  );
}
```

These components provide standard Material Design navigation patterns. Combine them appropriately to build intuitive user flows. Remember to manage state (like drawer open/close, selected tab, menu anchor) in your React components.

*(Refer to the official MUI documentation for Navigation components.)*