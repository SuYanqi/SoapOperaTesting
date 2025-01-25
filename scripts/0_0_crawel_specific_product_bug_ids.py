from bug_automating.utils.crawel_util import CrawelUtil


if __name__ == "__main__":
    """
    crawel all bug ids under specific product and component
    save bug ids in bug_ids.txt
    """
    product = "Fenix"
    component = None
    CrawelUtil.get_specific_product_component_bug_ids(product, component)
