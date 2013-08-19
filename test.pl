#!/usr/bin/perl

use strict;
use warnings;
use v5.10;

use Clang;

my $index = Clang::Index -> new(1);

#my $tunit = $index -> parse('/usr/include/w32api/windows.h');
my $tunit = $index -> parse('test.h');
my $nodes = $tunit -> cursor -> children;

sub trace
{
    my ($level, $nodes) = @_;
    foreach my $node (@$nodes) {
        say ' ' x $level, join(':', $node -> spelling, $node->displayname, $node->kind->spelling, $node->type->is_const ? 'const' : '', $node->type->is_volatile ? 'volatile' : '', $node->type->kind->spelling);
        trace($level + 1, $node->children) if defined $node->children;
#        trace($level + 1, [ $node->type->declaration ]) if defined $node->type->declaration && $node->spelling ne $node->type->declaration->spelling;
        say $node->type->declaration->displayname if defined $node->type->declaration;
    }
}

trace(0, $nodes);
