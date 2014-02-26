import flask

blueprint = flask.Blueprint("beverages", __name__)

@blueprint.route('/coffee')
def coffee():
    raise ex.ImATeapot()  # I really agreed to this whole project just for an excuse to do this....


@blueprint.route('/tea')
def tea():
       return '''
                           (
            _           ) )
         _,(_)._        ((
    ___,(_______).        )
  ,'__.   /       \    /\_
 /,' /  |""|       \  /  /
| | |   |__|       |,'  /
 \`.|                  /
  `. :           :    /
    `.            :.,'
      `-.________,-'
'''
