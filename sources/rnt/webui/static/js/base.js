function stack_onload(f) {
    var old = window.onload;
    if (typeof window.onload != 'function')
        window.onload = f;
    else
        window.onload = function() {
            if (old)
                old()
            f();
        }
}