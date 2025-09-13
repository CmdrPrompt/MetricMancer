class ReportWriter:
    """
    Utility class for writing report output to files.
    """
    @staticmethod
    def write_html(html, output_file):
        """
        Write the given HTML string to the specified output file.
        Args:
            html: The HTML content to write.
            output_file: The path to the output file.
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
