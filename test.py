import unittest, os, tempfile
import regex_read, generate, formats

test_dir = 'test'

test_format_dir = os.path.join(test_dir, 'format')
test_img_dir = os.path.join(test_dir, 'img')

def apply_parsed(func, t):
    for f in [ formats.format_punctuations,
               formats.format_numbers ]:
      t = f(t)
    post, news_items = regex_read.parse(t)
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
        with open(os.path.join(base_dir, 'input', f), in_mode) as i, \
             open(os.path.join(base_dir, 'out', name + (out_ext or ext)), out_mode) as o:
            yield i, o

def full_format(t):
    return apply_parsed(regex_read.lay_out, t)

def gen_image(t, out_path):
    return apply_parsed(
        lambda p, i: generate.generate_image(p, i, out_path),
        t
    )

class TestFormatting(unittest.TestCase):
    maxDiff = None

    def test_samples(self):
        for i, o in open_input_outputs(test_format_dir):
            self.assertEqual(full_format(i.read()), o.read())

class TestImages(unittest.TestCase):
    def test_samples(self):
        for i, o in open_input_outputs(test_img_dir, '.png', out_mode='rb'):
            with tempfile.NamedTemporaryFile(suffix='.png') as tf:
                gen_image(i.read(), tf.name)
                self.assertEqual(tf.read(), o.read())

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['gen']:
        for i, o in open_input_outputs(test_format_dir, out_mode='w'):
            o.write(full_format(i.read()))

        for i, o in open_input_outputs(test_img_dir, '.png', out_mode='wb'):
            gen_image(i.read(), o.name)
    else:
        unittest.main()
