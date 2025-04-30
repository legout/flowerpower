# Effects & Animations

Using jQuery's built-in methods for common visual effects and custom animations.

## Basic Effects

These methods change `display` or `opacity` and often involve animation.

*   **Visibility:**
    *   `.show([duration], [easing], [callback])`: Displays element(s).
    *   `.hide([duration], [easing], [callback])`: Hides element(s) (`display: none`).
    *   `.toggle([duration], [easing], [callback])`: Toggles between showing and hiding.
*   **Fading:**
    *   `.fadeIn([duration], [easing], [callback])`: Fades in (opacity 0 to 1).
    *   `.fadeOut([duration], [easing], [callback])`: Fades out (opacity 1 to 0, then `display: none`).
    *   `.fadeToggle([duration], [easing], [callback])`: Toggles fade in/out.
    *   `.fadeTo(duration, opacity, [easing], [callback])`: Fades to a specific `opacity` (0 to 1). Does *not* change `display`.
*   **Sliding:**
    *   `.slideDown([duration], [easing], [callback])`: Slides down into view (animates height).
    *   `.slideUp([duration], [easing], [callback])`: Slides up out of view (animates height, then `display: none`).
    *   `.slideToggle([duration], [easing], [callback])`: Toggles slide up/down.

**Common Parameters:**

*   `duration` (Optional): Milliseconds (e.g., `400`) or keywords (`'slow'`, `'fast'`). Default: `400`.
*   `easing` (Optional): Animation curve. Defaults: `'swing'`. `'linear'` also built-in. (Requires jQuery UI or plugins for more options).
*   `callback` (Optional): Function executed after animation completes for each element.

```javascript
$(function() {
  $('#toggleBtn').on('click', function() {
    $('#myElement').slideToggle('slow', function() {
      console.log('Slide toggle finished!'); // Callback example
    });
  });

  $('#fadeBtn').on('click', function() {
    $('#anotherElement').fadeToggle();
  });
});
```

## Custom Animations (`.animate()`)

Create custom animations on specific numeric CSS properties.

*   **Syntax:** `.animate(properties, [duration], [easing], [callback])`
*   **`properties`:** Object of target CSS properties and their final numeric values.
    *   Use camelCase for CSS properties (e.g., `marginLeft`, `fontSize`).
    *   Values: Numeric (e.g., `50`, `0.5`) or relative strings (`'+=50px'`, `'-=10'`).
    *   Special value `'toggle'` can be used for `height` and `width`.
    *   Animatable properties include `opacity`, `height`, `width`, `top`, `left`, `fontSize`, `margin*`, `padding*`, `scrollTop`, `scrollLeft`.
    *   Color animation usually requires jQuery UI or plugins.

```javascript
$(function() {
  $('#animateBtn').on('click', function() {
    $('#box')
      .animate({
        opacity: 0.5,
        marginLeft: '+=50px', // Move right relative to current position
        height: 'toggle'
      }, 1000, 'linear', function() { // Duration, Easing, Callback
        console.log('Box animation finished.');
      })
      .animate({ width: '50px' }, 'fast'); // Chain another animation
  });
});
```

## Animation Queue & Control

*   jQuery maintains an animation queue (`fx`) per element. Chained animations run sequentially by default.
*   **`.stop([clearQueue], [jumpToEnd])`:** Stops the *current* animation.
    *   `clearQueue` (boolean, default `false`): If `true`, removes remaining animations from the queue.
    *   `jumpToEnd` (boolean, default `false`): If `true`, immediately completes the current animation to its end state.
*   **`.delay(duration)`:** Adds a delay (milliseconds) to the animation queue.

```javascript
$('#myElement')
  .slideUp(500)
  .delay(200) // Wait 200ms
  .slideDown(500);

$('#stopBtn').on('click', function() {
  // Stop current animation, clear queue, jump to end state of current animation
  $('#myElement').stop(true, true);
});
```

**Note:** While jQuery effects are convenient, modern CSS transitions and animations are often more performant for simple visual changes. Use jQuery animations when complex sequencing, dynamic values, or callbacks are required.