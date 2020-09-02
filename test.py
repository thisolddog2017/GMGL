import unittest, os
import regex_read, formats

sample_dir = 'test'

def full_format(t):
    for f in [ formats.format_punctuations,
               formats.format_numbers ]:
      t = f(t)
    post, news_items = regex_read.parse(t)
    return regex_read.lay_out(post, news_items)

class TestFormatting(unittest.TestCase):
    maxDiff = None

    def test_samples(self):
        for f in os.listdir(os.path.join(sample_dir, 'input')):
            with open(os.path.join(sample_dir, 'input',f)) as i, \
                 open(os.path.join(sample_dir, 'out', f)) as o:
                self.assertEqual(full_format(i.read()), o.read())

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['gen']:
        for f in os.listdir(os.path.join(sample_dir, 'input')):
            with open(os.path.join(sample_dir, 'input',f)) as i, \
                 open(os.path.join(sample_dir, 'out', f), 'w') as o:
                o.write(full_format(i.read()))
    else:
        unittest.main()
