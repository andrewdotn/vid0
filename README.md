# vid0

A note-taking application for video content.

## Usage

This is a django app based on [django-boilerplate].

  - run `./manage.py runserver`
  - in `frontend/` run `yarn vite --port 3365`

Then add a series using the “Add a series” link, and add video files using
the ‘Add “…” videos” link.

[django-boilerplate]: https://github.com/andrewdotn/django-boilerplate

Shortcut keys in the viewer:

  - space bar to play/pause video
  - `f` to toggle full-screen
  - `s` to toggle subtitles
  - `n` to make a new note
  - `F1` to close the ‘new note’ screen—you can also hit escape, but if you
    are full-screen, that’ll exit full-screen mode instead, hence the
    shortcut key physically next to the escape key
  - `j`/`k` to step a frame at a time
  - `←`/`→` to skip 5 seconds back/forward
  - `c` to toggle cropping for pillarboxed video

## License

See `LICENSE`, which uses the same terms as the django project.
