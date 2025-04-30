# Material UI: Feedback Components (MUI Core)

Components for providing feedback to users about actions or system status.

## Core Concept

MUI Core offers components to communicate status, confirmation, or progress to users in ways that align with Material Design patterns, ranging from subtle snackbars to blocking dialogs.

**Key Feedback Components:**

*   **`<Alert>`:** Displays a short, important message in a way that attracts attention without interrupting the user task (e.g., success, error, warning, info).
*   **`<Dialog>`:** A modal window that requires user interaction to dismiss. Used for critical information, decisions, or tasks that block the main flow.
*   **`<Snackbar>`:** Provides brief, temporary messages (often at the bottom of the screen) about an app process. Typically includes an action or dismiss option.
*   **Progress Indicators (`<LinearProgress>`, `<CircularProgress>`):** Indicate the progress of an ongoing operation. Can be determinate (showing percentage) or indeterminate (showing activity).
*   **`<Skeleton>`:** Displays a placeholder preview of content before data has loaded, improving perceived performance.

**Importing:** Import components from `@mui/material`.

## Common Feedback Components

**1. `<Alert>`:**

*   **Props:** `severity` (`error`, `warning`, `info`, `success`), `variant` (`standard`, `filled`, `outlined`), `icon` (custom icon), `action` (e.g., an IconButton for closing), `onClose`. Use `<AlertTitle>` for a formatted title.

```jsx
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';

<Stack sx={{ width: '100%' }} spacing={2}>
  <Alert severity="error">
    <AlertTitle>Error</AlertTitle>
    This is an error alert — <strong>check it out!</strong>
  </Alert>
  <Alert severity="warning" action={
    <IconButton size="small" color="inherit" onClick={() => { /* handle close */ }}>
      <CloseIcon fontSize="inherit" />
    </IconButton>
  }>
    This is a warning alert.
  </Alert>
  <Alert severity="info" variant="filled">This is an info alert.</Alert>
  <Alert severity="success" variant="outlined">This is a success alert.</Alert>
</Stack>
```

**2. `<Dialog>`:**

*   Controlled component using `open` prop and `onClose` handler.
*   **Components:** `<Dialog>`, `<DialogTitle>`, `<DialogContent>`, `<DialogContentText>`, `<DialogActions>`.
*   **Props (`<Dialog>`):** `open`, `onClose`, `fullScreen`, `fullWidth`, `maxWidth` (`xs`, `sm`, `md`, `lg`, `xl`, `false`), `scroll` (`body`, `paper`).

```jsx
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import React from 'react';

function AlertDialog() {
  const [open, setOpen] = React.useState(false);
  const handleClickOpen = () => { setOpen(true); };
  const handleClose = () => { setOpen(false); };

  return (
    <React.Fragment>
      <Button variant="outlined" onClick={handleClickOpen}>Open alert dialog</Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{"Use Google's location service?"}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Let Google help apps determine location...
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Disagree</Button>
          <Button onClick={handleClose} autoFocus>Agree</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
```

**3. `<Snackbar>`:**

*   Controlled component using `open` prop and `onClose` handler. `onClose` receives `(event, reason)`, where `reason` can be `'timeout'`, `'clickaway'`, etc.
*   **Props:** `open`, `onClose`, `message` (simple text content), `autoHideDuration` (milliseconds), `action` (e.g., an "Undo" button or close icon), `anchorOrigin` (`{ vertical: 'top'|'bottom', horizontal: 'left'|'center'|'right' }`).
*   Often used with `<Alert>` component nested inside for richer content and severity indication.

```jsx
import Snackbar from '@mui/material/Snackbar';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Alert from '@mui/material/Alert'; // Use Alert inside Snackbar
import React from 'react';

function MySnackbar() {
  const [open, setOpen] = React.useState(false);
  const handleClick = () => { setOpen(true); };
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') { return; } // Don't close on click away
    setOpen(false);
  };

  const action = (
    <IconButton size="small" aria-label="close" color="inherit" onClick={handleClose}>
      <CloseIcon fontSize="small" />
    </IconButton>
  );

  return (
    <div>
      <Button onClick={handleClick}>Open Snackbar</Button>
      <Snackbar
        open={open}
        autoHideDuration={6000} // 6 seconds
        onClose={handleClose}
        message="Note archived" // Simple message example
        action={action}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
      {/* Example with Alert */}
      {/* <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="success" sx={{ width: '100%' }}>
          This is a success message!
        </Alert>
      </Snackbar> */}
    </div>
  );
}
```

**4. Progress Indicators:**

*   **`<CircularProgress>` & `<LinearProgress>`:**
*   **Props:** `variant` (`determinate`, `indeterminate` (default)), `value` (0-100, for determinate), `color`.

```jsx
import CircularProgress from '@mui/material/CircularProgress';
import LinearProgress from '@mui/material/LinearProgress';
import Box from '@mui/material/Box';

<Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
  <CircularProgress /> {/* Indeterminate */}
  <CircularProgress variant="determinate" value={75} /> {/* Determinate */}
  <LinearProgress /> {/* Indeterminate */}
  <LinearProgress variant="determinate" value={50} /> {/* Determinate */}
</Box>
```

**5. `<Skeleton>`:**

*   **Purpose:** Placeholder for content that is loading. Improves perceived performance.
*   **Props:** `variant` (`text` (default), `circular`, `rectangular`, `rounded`), `width`, `height`, `animation` (`pulse` (default), `wave`, `false`). Match skeleton shape/size to the content it replaces.

```jsx
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';

<Stack spacing={1}>
  {/* For variant="text", adjust the height via font-size */}
  <Skeleton variant="text" sx={{ fontSize: '1rem' }} />
  {/* For other variants, adjust width/height */}
  <Skeleton variant="circular" width={40} height={40} />
  <Skeleton variant="rectangular" width={210} height={60} />
  <Skeleton variant="rounded" width={210} height={60} />
</Stack>
```

Use feedback components appropriately: `Alert` for static messages, `Snackbar` for temporary notifications, `Dialog` for blocking interactions, `Progress`/`Skeleton` for loading states.

*(Refer to the official MUI documentation for Feedback components.)*