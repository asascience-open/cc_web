import urlparse
from cStringIO import StringIO

from flask import render_template, make_response, redirect, jsonify, flash, request, url_for
from cc_web import app

from compliance_checker.runner import ComplianceChecker

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def run_cc():

    # ensure vars
    err = False
    url = None
    if 'dataset-url' not in request.form or not request.form['dataset-url']:
        err = True
        flash("No dataset URL specified", 'error')
    else:
        url = request.form['dataset-url']
        try:
            u = urlparse.urlparse(url)
            assert u.scheme != ''
        except Exception as ex:
            err = True
            flash("Could not parse URL: %s" % ex, 'error')

    checkers = request.form.getlist('checkers')
    if len(checkers) == 0:
        err = True
        flash("You must specify one or more checkers", 'error')

    if err:
        return redirect(url_for('index'))

    ########
    # RUN CC

    output = ""

    csio = StringIO()
    try:
        # magic to wrap stdout
        with stdout_redirected(csio):
            ComplianceChecker.run_checker(url, checkers, 2, 'strict')

        output = csio.getvalue()

    except Exception as e:
        flash("Error while running Compliance Checker: %s" % e, 'error')
        return redirect(url_for('index'))
    finally:
        csio.close()

    return render_template('results.html', output=output)

# from: http://stackoverflow.com/a/14707227/84732
import sys
from contextlib import contextmanager
@contextmanager
def stdout_redirected(new_stdout):
    save_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout = save_stdout
