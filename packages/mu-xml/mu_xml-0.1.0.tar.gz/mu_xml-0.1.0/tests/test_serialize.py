from __future__ import annotations

import mu


class TestSerializeXml:

    def test_empty_element(self):
        assert mu.xml(["div"]) == "<div/>"


class TestAttributeFormatting:

    def test_escaping(self):
        # escape double quotes (required with foo="bar")
        assert (
            mu.XmlSerializer()._ser_attrs(["_", {"foo": '"hi"'}])
            == ' foo="&quot;hi&quot;"'
        )
        # note that one would expect this to be output as &apos;
        # but not a problem
        assert (
            mu.XmlSerializer()._ser_attrs(["_", {"foo": "'hi'"}])
            == ' foo="&#x27;hi&#x27;"'
        )
        # always escape &
        assert mu.XmlSerializer()._ser_attrs(["_", {"foo": "Q&A"}]) == ' foo="Q&amp;A"'
        # always escape < and >
        assert (
            mu.XmlSerializer()._ser_attrs(["_", {"foo": "<foo/>"}])
            == ' foo="&lt;foo/&gt;"'
        )


class TestElementTextFormatting:

    def test_escaping(self):
        pass


class TestCreateNode:

    def test_empty_element(self):
        assert mu.xml(["foo"]) == "<foo/>"

    def test_element_with_attributes(self):
        assert mu.xml(["foo", {"a": 10, "b": 20}]) == '<foo a="10" b="20"/>'

    def test_element_without_attributes(self):
        assert mu.xml(["foo", {}]) == "<foo/>"

    def test_element_with_content(self):
        assert mu.xml(["foo", "bla"]) == "<foo>bla</foo>"

    def test_element_with_content_and_attributes(self):
        assert (
            mu.xml(["foo", {"a": 10, "b": 20}, "bla"]) == '<foo a="10" b="20">bla</foo>'
        )

    def test_element_seq(self):
        assert mu.xml(["a"], ["b"], ["c"]) == "<a/><b/><c/>"


class TestDoc:

    def test_doc_with_empty_element(self):
        assert mu.xml(["foo", ["bar"]]) == "<foo><bar/></foo>"

    def test_doc_with_text_newlines(self):
        assert (
            mu.xml(["foo", ["bar", "foo", "\n", "bar", "\n"]])
            == "<foo><bar>foo\nbar\n</bar></foo>"
        )


class TestDocWithNamespaces:

    def test_doc_with_empty_element(self):
        assert (
            mu.xml(["x:foo", ["y:bar", {"m:a": 10, "b": 20}]])
            == '<x:foo><y:bar b="20" m:a="10"/></x:foo>'
        )


class TestDocWithSpecialNodes:

    def test_doc_with_comments(self):
        # FIXME no -- allowed
        assert mu.xml(["$comment", "bla&<>"]) == "<!-- bla&<> -->"

    def test_doc_with_cdata(self):
        # FIXME no ]]> allowed, could escape as ]]&gt;
        #       (in normal content already handled by always escaping >)
        assert mu.xml(["$cdata", "bla&<>"]) == "<![CDATA[bla&<>]]>"

    def test_doc_with_processing_instruction(self):
        # FIXME no ?> allowed
        assert (
            mu.xml(["$pi", 'xml version="1.0" encoding="UTF-8"'])
            == '<?xml version="1.0" encoding="UTF-8"?>'
        )

    def test_doc_with_invalid_special_node(self):
        assert mu.xml(["$foo", "bla"]) == ""


class TestTagFormatting:
    # FIXME html, xhtml have particular rules re self-closing or not
    #       these elements are:
    #       area, base, br, col, command, embed, hr, img, input, keygen,
    #       link, meta, param, source, track, wbr
    def test_empty_elements(self):
        assert mu.xml(["img"]) == "<img/>"
        assert mu.xml(["img", {"src": "foo"}]) == '<img src="foo"/>'


# https://github.com/weavejester/hiccup/blob/master/test/hiccup/compiler_test.clj


class TestCompile:

    def test_normal_tag_with_attrs(self):
        assert mu.xml(["p", {"id": 1}]) == '<p id="1"/>'

    def test_void_tag_with_attrs(self):
        assert mu.xml(["br", {"id": 1}]) == '<br id="1"/>'

    def test_normal_tag_with_content(self):
        assert mu.xml(["p", "x"]) == "<p>x</p>"

    def test_void_tag_with_content(self):
        assert mu.xml(["br", "x"]) == "<br>x</br>"

    def test_normal_tag_without_attrs(self):
        assert mu.xml(["p", {}]) == "<p/>"

    def test_void_tag_without_attrs(self):
        assert mu.xml(["br", {}]) == "<br/>"
        assert mu.xml(["br", None]) == "<br/>"


# https://github.com/weavejester/hiccup/blob/master/test/hiccup/core_test.clj


class TestTagNames:

    def basic_tags(self):
        assert mu.xml(["div"]) == "<div></div>"

    # def tag_syntactic_sugar(self):
    #     pass


class TestTagContents:

    def test_empty_tags(self):
        # NOTE default mode is XML, hiccup's default mode is XHTML
        assert mu.xml(["div"]) == "<div/>"
        assert mu.xml(["h1"]) == "<h1/>"
        assert mu.xml(["script"]) == "<script/>"
        assert mu.xml(["text"]) == "<text/>"
        assert mu.xml(["a"]) == "<a/>"
        assert mu.xml(["iframe"]) == "<iframe/>"
        assert mu.xml(["title"]) == "<title/>"
        assert mu.xml(["section"]) == "<section/>"
        assert mu.xml(["select"]) == "<select/>"
        assert mu.xml(["object"]) == "<object/>"
        assert mu.xml(["video"]) == "<video/>"

    def test_void_tags(self):
        assert mu.xml(["br"]) == "<br/>"
        assert mu.xml(["link"]) == "<link/>"
        assert mu.xml(["colgroup", {"span": 2}]) == '<colgroup span="2"/>'

    def test_containing_text(self):
        assert mu.xml(["text", "Lorem Ipsum"]) == "<text>Lorem Ipsum</text>"

    def test_contents_are_concatenated(self):
        assert mu.xml(["body", "foo", "bar"]) == "<body>foobar</body>"
        assert mu.xml(["body", ["p"], ["br"]]) == "<body><p/><br/></body>"
        # FIXME
        # assert (
        #    mu.xhtml(["body", ["p"], ["br"]])
        #    == "<body><p></p><br /></body>"
        # )

    def test_seqs_are_expanded(self):
        # FIXME
        # assert mu.xml(([["p", "a"],["p", "b"]])) == "<p>a</p><p>b</p>"
        pass

    def test_tags_can_contain_tags(self):
        assert mu.xml(["div", ["p"]]) == "<div><p/></div>"
        # FIXME
        # assert mu.xhtml(["div", ["p"]]) == "<div><p></p></div>"


class TestTagAttributes:

    def test_tag_with_blank_attribute_map(self):
        assert mu.xml(["xml", {}]) == "<xml/>"
        assert mu.xml(["xml", None]) == "<xml/>"

    def test_tag_with_populated_attribute_map(self):
        assert mu.xml(["xml", {"a": 123}]) == '<xml a="123"/>'
        assert mu.xml(["xml", {"a": 1, "b": 2, "c": 3}]) == '<xml a="1" b="2" c="3"/>'
        assert mu.xml(["img", {"id": 1}]) == '<img id="1"/>'
        # how to render this?
        assert mu.xml(["xml", {"a": ["kw", "foo", 3]}]) == '<xml a="kw foo 3"/>'

    def test_attribute_values_are_escaped(self):
        assert mu.xml(["div", {"id": "<>&"}]) == '<div id="&lt;&gt;&amp;"/>'

    def test_nil_attributes(self):
        assert mu.xml(["span", {"class": None}]) == "<span/>"

    def test_tag_with_vector_class(self):
        # TODO tests for syntactic sugar on element names
        pass


class TestRenderModes:

    def test_closed_tag(self):
        assert mu.xml(["p"], ["br"]) == "<p/><br/>"
