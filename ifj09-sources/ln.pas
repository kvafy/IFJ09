var
{--deleni--}
d1:double;
d2:double;
dd2:double;
d3:double;
epsmax:double;
eps:double;
minus:integer;
{--deleni--}
{--ln--}
e:double; { e }
em1:double; { e^-1 }
mocnina:integer;
lres:double;
lx:double;
lxx:double;
xn:double;
ep:double;
lnepsilon:double;
li:double;
sign:double;
lend:integer;
{--ln--}
begin
	e:=2.7182818284590452354;
	em1:=0.3678794411714423215955626751784;
	lnepsilon:=0.1e-10;
	epsmax:=0.1e-12;
	lend:=0;

	while lend=0 do
	begin
		readln(lx); { nacteni promenne ze vstupu }
		if lx < 0.0 then
		begin
			write('NAN'#10'');
			lend:=1
		end
		else if lx = 0.0 then
			write('-INF'#10'')
		else
		begin
			lxx:=lx;
			mocnina:=0;
			li:=1.0;
			while lxx >= e do
			begin
				lxx:=lxx*em1;
				mocnina:=mocnina+1
			end;
			while lxx <= em1 do
			begin
				lxx:=lxx*e;
				mocnina:=mocnina-1
			end;
			lres:=0.0;
			d1:=lxx-1.0;
			d2:=lxx+1.0;
			d3:=0.0;
			dd2:=0.0;
			eps:=128.0;
			if d1<0.0 then
				minus:=1
			else
				minus:=0;
			if d2<0.0 then
				minus:=minus-1
			else
				minus:=minus+0;
			if d1<0.0 then
				d1:=0.0-d1
			else begin end;
			if d2<0.0 then
				d2:=0.0-d2
			else begin end;
			while d1-dd2 > epsmax do
			begin
				while dd2 < d1 do
				begin
					d3:=d3+eps;
					dd2:=d2*d3
				end;
				d3:=d3-eps;
				dd2:=d2*d3;
				eps:=eps*0.5
			end;
			if minus<>0 then
				d3:=0.0-d3
			else
				begin end;
			xn:=d3;
			ep:=xn;
			if lx<1.0 then
				sign:=0.0-1.0
			else
				sign:=1.0;
			while ep*sign > lnepsilon do
			begin
				d1:= ep;
				d2:= li;
				d3:=0.0; { podil }
				dd2:=0.0; { zkusebni vysledek d3*d2 }
				eps:=128.0; { pocatecni krok pricitani }
				if d1<0.0 then
					minus:=1
				else
					minus:=0;
				if d2<0.0 then
					minus:=minus-1
				else
					minus:=minus+0;
				if d1<0.0 then
					d1:=0.0-d1
				else begin end;
				if d2<0.0 then
					d2:=0.0-d2
				else begin end;
				while d1-dd2 > epsmax do
				begin
					while dd2 < d1 do
					begin
						d3:=d3+eps;
						dd2:=d2*d3
					end;
					d3:=d3-eps;
					dd2:=d2*d3;
					eps:=eps*0.5
				end;
				if minus<>0 then
					d3:=0.0-d3
				else
					begin end;
				lres:=lres + d3;
				ep:=ep*xn*xn;
				li:=li+2
			end;
			lres:=lres*2 + mocnina;
			write(lres, ''#10'')
		end
	end
end.
