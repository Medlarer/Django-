from django.template import Library
from django.forms.boundfield import BoundField
from django.db.models import QuerySet
from django.forms import ModelChoiceField
from django.urls import reverse
from stark.service import v1


register=Library()

@register.inclusion_tag("stark/form.html")
def pop_key(forms,config=None):
    new_forms = []
    for field_name in forms:
        temp = {"is_pop": False, "url": None, "field_name": field_name}
        if isinstance(field_name.field, ModelChoiceField):
            # print(field_name.field, type(field_name.field))
            related_class = field_name.field.queryset.model
            if related_class in v1.site._registry:
                # print(11111,config)
                if config:
                    model_name=config.model_class._meta.model_name
                    # print(1,model_name)
                    related_name=config.model_class._meta.get_field(field_name.name).rel.related_name
                    app_model_name = (related_class._meta.app_label, related_class._meta.model_name)
                    base_url = reverse("stark:%s_%s_add" % (app_model_name))
                    pop_url = "%s?tag_id=%s&model_name=%s&related_name=%s" % (base_url, field_name.auto_id,model_name,related_name)
                    temp["is_pop"] = True
                    temp["url"] = pop_url
        new_forms.append(temp)
        # yield {"forms":temp}
    # print({"forms":new_forms})
    return {"forms":new_forms}
