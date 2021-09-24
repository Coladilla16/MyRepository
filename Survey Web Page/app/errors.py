from flask import render_template


def handle_404(e):
    return render_template("main/errors.html", error_code=404)


def handle_403(e):
    return render_template("main/errors.html", error_code=403)


def handle_500(e):
    # TODO: Log error or email admin
    return render_template("main/errors.html", error_code=500)
