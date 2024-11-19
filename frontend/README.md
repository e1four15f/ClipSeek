# Frontend

ClipSeek's frontend is a lightweight, component-based single-page application designed to facilitate intuitive search and exploration of video clips. Built with **Svelte**, **TailwindCSS**, and **Flowbite**.

### Components

1. **SearchForm.svelte**

- Collects search input (text, file, or reference).
- Triggers backend search API via `/search/by_text`, `/search/by_file`, or `/search/by_reference`.

2. **Gallery.svelte**

- Displays results in an infinite scroll layout.
- Dynamically fetches more results from the backend through `/search/continue`.

3. **MediaView.svelte**

- Modal component displaying detailed clip information.
- Integrates `Plyr` player and offers functionality for finding similar clips.

4. **Logging.svelte**

- Displays toast notifications to communicate system events and errors.

## Developing

To start developing, you have the option to use a docker container or develop locally. Following is the setup for the local environment.

Install npm dependencies

```bash
make install
```

Run the development server

```bash
make run
```

Prettify the code

```bash
make pretty
```
