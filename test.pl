use utf8;
use Encode;

open my $fh, '>', 'ソフト開発.txt';
print $fh Encode::encode('utf-8', "ソフト開発\n");
close $fh;

rename 'ソフト開発.txt' => 'ソフト開発_.txt';

print join(' ', stat('ソフト開発_.txt')), "\n";

opendir DIR, '.';
print join(' ', map { Encode::encode('cp932', $_) } grep { /\.txt/ } readdir DIR), "\n";
