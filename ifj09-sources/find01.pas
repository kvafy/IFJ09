{ cte ze vstupu N dvojic retezcu (str1, str2) a vypise na vlastni radek
  pozici retezce str2 v str1}
var
    N : integer;
    i : integer;
	str1 : string;
	str2 : string;
begin
	readln(N);
	i := 0;
	str2 := 'bca';
	write('sort demo: ', str2, ' -> ', sort(str2), ''#10'');
	
	while(i < N) do
	begin
	    readln(str1);
	    readln(str2);
	    write(find(str1,str2), ''#10'');
	    i := i + 1
	end
end.

