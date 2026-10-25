# WP-MXK-0003 — Release and vendoring contract

Lets any meta-harness, even one with no network at all, prove with one offline command that
its copy of the kernel is exactly a released kernel and still behaves correctly. Kernel
releases pin every file by hash and carry their own verifier. They also carry their own test
runner, so no outside package is needed. Every future change must stay releasable, because
CI builds and verifies a release on every pull request.
