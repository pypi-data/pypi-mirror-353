from __future__ import annotations

from typing import Type, TYPE_CHECKING, get_origin, get_args

from pydantic import BaseModel

if TYPE_CHECKING:
    from ..admin import Admin


def get_default_column_renderers() -> list[Type[ModelColumnRenderer]]:
    # NB: order matters (first one handling it wins)
    return [
        ModelColumnRenderer,
    ]


class ColumnRenderer:
    @classmethod
    def handles(cls, admin: Admin, ModelType: BaseModel, column: dict[str, str]):
        """
        Return True if this renderer can render the column 'key' in `ModelType`.
        """
        return False

    def __init__(self, admin: Admin, ModelType: BaseModel, column: dict[str, str]):
        super(ColumnRenderer).__init__()
        self.admin = admin
        self.ModelType = ModelType
        self.column = column

    def apply(self, table):
        raise NotImplementedError()


class ModelColumnRenderer(ColumnRenderer):
    @classmethod
    def handles(cls, admin: Admin, ModelType: Type[BaseModel], column: dict[str, str]):
        """
        Return True if this renderer can render the column 'key' in `ModelType`.
        """
        field_name = column["field"]
        field = ModelType.model_fields.get(field_name)
        if field is None:
            return False
        for Type in get_args(field.annotation):
            if admin.has_view_for(Type):
                return True
        return False

    def apply(self, table):
        print("APPLY", self, self.column)
        card_prefix = f"{self.admin.prefix}/{self.ModelType.__name__}"
        table.add_slot(
            f"body-cell-{self.column['field']}",
            f"""
            <q-td :props="props">
                <q-chip esize="xs">
                <a :href="'{card_prefix}/'+props.row.name.value">{{{{ props.value }}}}</a>
                </q-chip>
            </q-td>
            """,
        )

        # table.add_slot(
        #     f"body-cell-{self.column['name']}",
        #     f"""
        #     <q-td :props="props">
        #         <q-chip esize="xs">
        #         <a :href="'{card_prefix}/'+props.row.__pk__">{{{{ props.value }}}}</a>
        #         </q-chip>
        #     </q-td>
        #     """,
        # )
