# WP-MXK-0002 — Bring in the enforcement core

The enforcement core was built and independently reviewed in the source meta-harness. This
package moves it here, where the kernel now lives, and makes it fully self-contained:
nothing in it reaches outside its own folder or beyond the Python standard library. That
is the property every vendored copy, air-gapped ones included, will depend on.
