# Gate commands by ecosystem

Use these only when the project documents no command of its own. `SKILL.md` step 4 links here.

| Ecosystem | Detect via | Type-check · lint · format · test |
| --- | --- | --- |
| JS/TS | `package.json` and lockfile (`bun.lock` bun, `pnpm-lock` pnpm, `yarn.lock` yarn, else npm) | `<pm> run type-check` · `lint` · `fmt`/`format` · `test` |
| Rust | `Cargo.toml` | `cargo check` · `cargo clippy -- -D warnings` · `cargo fmt --check` · `cargo test` |
| Go | `go.mod` | `go vet ./...` · `golangci-lint run` · `gofmt -l .` · `go test ./...` |
| Python | `pyproject.toml`/`setup.cfg` | `mypy`/`pyright` · `ruff check` · `ruff format --check` · `pytest` |
| Java/Kotlin | `pom.xml`/`build.gradle` | `mvn verify` / `gradle build check` |
