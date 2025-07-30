import pytest
import pytest_asyncio

from odata_v4_query.errors import (
    TwoArgumentsExpectedError,
    UnexpectedEmptyArgumentsError,
    UnexpectedNullFiltersError,
    UnexpectedNullFunctionNameError,
    UnexpectedNullOperandError,
    UnexpectedNullOperatorError,
    UnknownFunctionError,
    UnknownOperatorError,
)
from odata_v4_query.filter_parser import FilterNode
from odata_v4_query.query_parser import ODataQueryOptions, ODataQueryParser
from odata_v4_query.utils.beanie import apply_to_beanie_query

from ._core.beanie import User, UserProjection, get_client, seed_data


@pytest_asyncio.fixture(autouse=True)
async def client():
    client = await get_client()
    await seed_data()
    return client


class TestBeanie:
    parser = ODataQueryParser()

    @pytest.mark.asyncio
    async def test_skip(self):
        users_count = len(await User.find().to_list())
        options = self.parser.parse_query_string('$skip=2')
        query = apply_to_beanie_query(options, User.find())
        result = await query.to_list()
        assert len(result) == users_count - 2
        assert result[0].name == 'Alice'

    @pytest.mark.asyncio
    async def test_top(self):
        options = self.parser.parse_query_string('$top=2')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 2
        assert result[0].name == 'John'
        assert result[1].name == 'Jane'

    @pytest.mark.asyncio
    async def test_page(self):
        users_count = len(await User.find().to_list())

        # default top
        options = self.parser.parse_query_string('$page=1')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == users_count

        # top 3
        options = self.parser.parse_query_string('$page=1&$top=4')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 4
        options = self.parser.parse_query_string('$page=2&$top=4')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 4
        options = self.parser.parse_query_string('$page=3&$top=4')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 2
        options = self.parser.parse_query_string('$page=4&$top=4')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_filter(self):
        # comparison and logical
        options = self.parser.parse_query_string("$filter=name eq 'John' and age ge 25")
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 1
        assert result[0].name == 'John'

        options = self.parser.parse_query_string('$filter=age lt 25 or age gt 35')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 4

        options = self.parser.parse_query_string("$filter=name in ('Eve', 'Frank')")
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 2
        assert result[0].name == 'Eve'
        assert result[1].name == 'Frank'

        options = self.parser.parse_query_string("$filter=name nin ('Eve', 'Frank')")
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 8

        options = self.parser.parse_query_string(
            "$filter=name ne 'John' and name ne 'Jane'"
        )
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 8

        options = self.parser.parse_query_string(
            "$filter=not name eq 'John' and not name eq 'Jane'"
        )
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 8

        options = self.parser.parse_query_string('$filter=name eq null')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 0

        options = self.parser.parse_query_string('$filter=name ne null')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 10

        # string functions
        options = self.parser.parse_query_string(
            "$filter=startswith(name, 'J') and age ge 25"
        )
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 2
        assert result[0].name == 'John'
        assert result[1].name == 'Jane'

        options = self.parser.parse_query_string("$filter=endswith(name, 'e')")
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 5
        assert result[0].name == 'Jane'
        assert result[1].name == 'Alice'
        assert result[2].name == 'Charlie'
        assert result[3].name == 'Eve'
        assert result[4].name == 'Grace'

        options = self.parser.parse_query_string(
            "$filter=contains(name, 'i') and age le 35"
        )
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 2
        assert result[0].name == 'Alice'
        assert result[0].age == 35
        assert result[1].name == 'Charlie'
        assert result[1].age == 32

        # collection
        options = self.parser.parse_query_string("$filter=addresses has '101 Main St'")
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 2
        assert result[0].name == 'Alice'
        assert result[1].name == 'Bob'

    @pytest.mark.asyncio
    async def test_search(self):
        options = self.parser.parse_query_string('$search=John')
        query = apply_to_beanie_query(options, User, search_fields=['name', 'email'])
        result = await query.to_list()
        assert len(result) == 1
        assert result[0].name == 'John'

    @pytest.mark.asyncio
    async def test_orderby(self):
        options = self.parser.parse_query_string('$orderby=name asc,age desc')
        query = apply_to_beanie_query(options, User)
        result = await query.to_list()
        assert len(result) == 10
        assert result[0].name == 'Alice'
        assert result[1].name == 'Bob'
        assert result[1].age == 40
        assert result[2].name == 'Bob'
        assert result[2].age == 28
        assert result[3].name == 'Charlie'
        assert result[4].name == 'David'
        assert result[5].name == 'Eve'
        assert result[6].name == 'Frank'
        assert result[7].name == 'Grace'
        assert result[8].name == 'Jane'
        assert result[9].name == 'John'

    @pytest.mark.asyncio
    async def test_select(self):
        options = self.parser.parse_query_string('$select=name,email')
        query = apply_to_beanie_query(options, User, parse_select=True)
        result = await query.to_list()
        assert len(result) == 10
        assert result[0]['name'] == 'John'
        assert result[0]['email'] == 'john@example.com'

    @pytest.mark.asyncio
    async def test_projection(self):
        options = self.parser.parse_query_string('$top=1')
        query = apply_to_beanie_query(options, User, projection_model=UserProjection)
        result = await query.to_list()
        assert len(result) == 1
        assert isinstance(result[0], UserProjection)
        assert result[0].name == 'John'
        assert result[0].email == 'john@example.com'

        options = self.parser.parse_query_string('$top=1&$select=name,email')
        query = apply_to_beanie_query(
            options, User, projection_model=UserProjection, parse_select=True
        )
        result = await query.to_list()
        assert len(result) == 1
        assert isinstance(result[0], UserProjection)
        assert result[0].name == 'John'
        assert result[0].email == 'john@example.com'

    def test_unexpected_null_filters(self):
        options = ODataQueryOptions(filter_=FilterNode(type_='value'))
        with pytest.raises(UnexpectedNullFiltersError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_operator(self):
        options = ODataQueryOptions(filter_=FilterNode(type_='operator'))
        with pytest.raises(UnexpectedNullOperatorError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_operand(self):
        options = ODataQueryOptions(filter_=FilterNode(type_='operator', value='eq'))
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_operand_value(self):
        options = ODataQueryOptions(
            filter_=FilterNode(
                type_='operator',
                value='eq',
                left=FilterNode(type_='identifier'),
                right=FilterNode(type_='literal', value='John'),
            )
        )
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_operand_for_in_nin_operators(self):
        options1 = ODataQueryOptions(
            filter_=FilterNode(
                type_='operator',
                value='in',
                left=FilterNode(type_='identifier', value='name'),
                right=FilterNode(type_='list'),
            )
        )
        options2 = ODataQueryOptions(
            filter_=FilterNode(
                type_='operator',
                value='nin',
                left=FilterNode(type_='identifier', value='name'),
                right=FilterNode(type_='list'),
            )
        )
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options1, User)
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options2, User)

    def test_unexpected_null_operand_for_has_operator(self):
        options = ODataQueryOptions(
            filter_=FilterNode(
                type_='operator',
                value='has',
                left=FilterNode(type_='identifier', value='addresses'),
                right=FilterNode(type_='literal'),
            )
        )
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_operand_for_and_or_operators(self):
        options1 = ODataQueryOptions(filter_=FilterNode(type_='operator', value='and'))
        options2 = ODataQueryOptions(filter_=FilterNode(type_='operator', value='or'))
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options1, User)
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options2, User)

    def test_unexpected_null_operand_for_not_nor_operators(self):
        options1 = ODataQueryOptions(filter_=FilterNode(type_='operator', value='not'))
        options2 = ODataQueryOptions(filter_=FilterNode(type_='operator', value='nor'))
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options1, User)
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options2, User)

    def test_unknown_operator(self):
        options = ODataQueryOptions(
            filter_=FilterNode(type_='operator', value='unknown')
        )
        with pytest.raises(UnknownOperatorError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_function_name(self):
        options = ODataQueryOptions(filter_=FilterNode(type_='function'))
        with pytest.raises(UnexpectedNullFunctionNameError):
            apply_to_beanie_query(options, User)

    def test_unexpected_empty_arguments(self):
        options = ODataQueryOptions(
            filter_=FilterNode(type_='function', value='startswith')
        )
        with pytest.raises(UnexpectedEmptyArgumentsError):
            apply_to_beanie_query(options, User)

    def test_two_arguments_expected(self):
        options = ODataQueryOptions(
            filter_=FilterNode(
                type_='function',
                value='startswith',
                arguments=[
                    FilterNode(type_='identifier', value='name'),
                    FilterNode(type_='literal', value='J'),
                    FilterNode(type_='literal', value='J'),
                ],
            )
        )
        with pytest.raises(TwoArgumentsExpectedError):
            apply_to_beanie_query(options, User)

    def test_unexpected_null_operand_for_function(self):
        options = ODataQueryOptions(
            filter_=FilterNode(
                type_='function',
                value='startswith',
                arguments=[
                    FilterNode(type_='identifier', value='name'),
                    FilterNode(type_='literal'),
                ],
            )
        )
        with pytest.raises(UnexpectedNullOperandError):
            apply_to_beanie_query(options, User)

    def test_unknown_function(self):
        options = ODataQueryOptions(
            filter_=FilterNode(
                type_='function',
                value='unknown',
                arguments=[
                    FilterNode(type_='identifier', value='name'),
                    FilterNode(type_='literal', value='J'),
                ],
            )
        )
        with pytest.raises(UnknownFunctionError):
            apply_to_beanie_query(options, User)
