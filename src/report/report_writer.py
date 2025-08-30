class ReportWriter:
    @staticmethod
    def write_html(html, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
