#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import Any

from flask import Blueprint, Flask
from flask_assets import Bundle, Environment

# version is same as tabler-icons
__version__ = "3.34.0"


class TablerIcons:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["tabler_icons"] = self
        bp = Blueprint(
            "tabler_icons",
            __name__,
            static_folder="static/tabler_icons",
            static_url_path=f"/tabler_icons{app.static_url_path}",
            template_folder="templates",
        )
        app.jinja_env.globals["tabler_icons"] = self
        app.config.setdefault("TABLER_ICON_SIZE", 24)
        app.register_blueprint(bp)

        # use webassets for hosting
        assets = Environment(app)

        svg = Bundle(
            "tabler_icons/tabler-sprite-nostroke.svg", output="gen/tabler_icons/tabler-sprite-nostroke.svg"
        )
        assets.register("tabler_icons_nostroke", svg)

        svg = Bundle(
            "tabler_icons/tabler-sprite-filled.svg", output="gen/tabler_icons/tabler-sprite-filled.svg"
        )
        assets.register("tabler_icons_filled", svg)
        self.assets_url = dict(
            filled=assets["tabler_icons_filled"].urls()[0],
            normal=assets["tabler_icons_nostroke"].urls()[0],
        )
