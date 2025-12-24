from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    price_decimal = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Цена",
        help_text="Цена в рублях/долларах",
    )

    class Meta:
        model = Item
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial["price_decimal"] = self.instance.price_decimal

    def save(self, commit=True):
        price_decimal = self.cleaned_data.get("price_decimal")
        if price_decimal is not None:
            self.instance.price = int(price_decimal * 100)
        return super().save(commit)
