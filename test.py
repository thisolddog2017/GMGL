import unittest, os, tempfile
import text_read, generate, text_process, layout, markdown

test_dir = 'test'

test_text_dir = os.path.join(test_dir, 'text')
test_img_dir = os.path.join(test_dir, 'img')
test_md_dir = os.path.join(test_dir, 'md')

def apply_parsed(func, t):
    for f in [ text_process.format_punctuations,
               text_process.format_numbers ]:
      t = f(t)
    post, news_items = text_read.parse(t)
    return func(post, news_items)

def open_input_outputs(base_dir, out_ext=None, in_mode='r', out_mode='r'):
    """
    Loop through <base_dir>/input and <base_dir>/out, yield
    consecutive pairs of opened input / output files.
    Input files need to exist beforehand.

    base_dir : the base directory where the input / output files should reside
    out_ext : the output file extension, if None, use the same as input file
    in_mode : input file open mode
    out_mode : output file open mode
    """
    for f in os.listdir(os.path.join(base_dir, 'input')):
        name, ext = os.path.splitext(f)
        o_ext = out_ext or ext
        with open(os.path.join(base_dir, 'input', f), in_mode) as i, \
             open(os.path.join(base_dir, 'out', name + o_ext), out_mode) as o:
            print('{}{{{},{}}}'.format(name, ext, o_ext))
            yield i, o

def full_text_process(t):
    return apply_parsed(layout.layout_text, t)

def gen_image(t, out_path):
    return apply_parsed(
        lambda p, i: generate.generate_image(p, i, out_path),
        t
    )

class TestTextProcess(unittest.TestCase):
    maxDiff = None

    def test_samples(self):
        for i, o in open_input_outputs(test_text_dir):
            self.assertEqual(full_text_process(i.read()), o.read())

class TestImages(unittest.TestCase):
    def test_samples(self):
        from PIL import Image
        from PIL import ImageChops
        for i, o in open_input_outputs(test_img_dir, '.png', out_mode='rb'):
            with tempfile.NamedTemporaryFile(suffix='.png') as tf:
                gen_image(i.read(), tf.name)
                # https://stackoverflow.com/a/56280735
                self.assertFalse(
                    ImageChops.difference(Image.open(tf), Image.open(o)).getbbox(),
                    "Generated image different from {}".format(o.name)
                )

class TestMarkdown(unittest.TestCase):
    def test_samples(self):
        for i, o in open_input_outputs(test_md_dir):
            self.assertEqual(markdown.markdown_to_plaintext(i.read()), o.read())

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['gen']:
        for i, o in open_input_outputs(test_text_dir, out_mode='w'):
            o.write(full_text_process(i.read()))

        for i, o in open_input_outputs(test_img_dir, '.png', out_mode='wb'):
            gen_image(i.read(), o.name)

        for i, o in open_input_outputs(test_md_dir, out_mode='w'):
            o.write(markdown.markdown_to_plaintext(i.read()))

    else:
        unittest.main(verbosity=2)
