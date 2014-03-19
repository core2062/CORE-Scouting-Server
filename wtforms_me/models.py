from wtforms import Form


class ModelForm(Form):
    """A WTForms mongoengine model form"""

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.instance = (kwargs.pop('instance', None) or kwargs.get('obj', None))
        if self.instance and not formdata:
            obj = self.instance
        self.formdata = formdata
        super(ModelForm, self).__init__(formdata, obj, prefix, **kwargs)

    def validate(self):
        flag = True
        if not super(ModelForm, self).validate():
            flag = False
        if not self.instance:
            self.instance = self.model_class()
        for k, v in self._fields.iteritems():
            if v.errors:
                continue
            try:
                self.instance._fields[k].validate(self.data.get(k))
            except Exception, e:
                v.errors.append(e.message)
                flag = False
        return flag
        

    def save(self, commit=True, **kwargs):
        if self.instance:
            self.populate_obj(self.instance)
        else:
            self.instance = self.model_class(**self.data)

        if commit:
            self.instance.save(**kwargs)
        return self.instance
