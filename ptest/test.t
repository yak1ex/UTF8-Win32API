use Test::More tests => 12;

BEGIN {
use_ok('utf8');
use_ok('Encode');
}

my @st;
my $fh;

ok(open($fh, '>', 'ソフト開発.txt'), 'open');
print $fh Encode::encode('utf-8', "ソフト開発\n");
close $fh;

@st = stat 'ソフト開発.txt';
ok(@st, 'stat');

ok(rename('ソフト開発.txt' => 'ソフト開発_.txt'), 'rename');

@st = stat 'ソフト開発.txt';
ok(!@st, 'stat for old');
@st = stat 'ソフト開発_.txt';
ok(@st, 'stat for new');

opendir DIR, '.';
my @gr = grep { /ソフト開発_\.txt/ } readdir DIR;
closedir DIR;
ok(@gr == 1, 'readdir');

unlink 'ソフト開発_.txt';
@st = stat 'ソフト開発_.txt';
ok(!@st, 'unlink');

ok(system('.\\ptest\\probe.exe > NUL') == 0, 'system');

{
    local %ENV = ('TEST' => 'テスト');
    my $result = `.\\ptest\\probe.exe`;
    # Assuming CP932 environment
    like($result, qr/\[ENV\].*544553543D836583588367\s*\[ARGV\]/s, 'backquote with %ENV');
}

{
    local %ENV = ();
    my $result = `.\\ptest\\probe.exe テスト`;
    # Assuming CP932 environment
    like($result, qr/\[ENV\]\s+\[ARGV\].*\s+836583588367/s, 'backquote with args');
}
