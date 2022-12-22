PyChem
======
~~[wheel (GitLab)](https://gitlab.com/KOLANICH-mirrors/PyChem/-/jobs/artifacts/master/raw/dist/PyChem-0.CI-py3-none-any.whl?job=build)~~
[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-mirrors/PyChem/workflows/CI/master/PyChem-0.CI-py3-none-any.whl)
~~![GitLab Build Status](https://gitlab.com/KOLANICH-mirrors/PyChem/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH-mirrors/PyChem/badges/master/coverage.svg)~~
[![GitHub Actions](https://github.com/KOLANICH-mirrors/PyChem/workflows/CI/badge.svg)](https://github.com/KOLANICH-mirrors/PyChem/actions/)
[![PyPI legacy page](https://img.shields.io/pypi/wheel/PyChem)](https://pypi.org/project/PyChem/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-mirrors/PyChem.svg)](https://libraries.io/github/KOLANICH-mirrors/PyChem)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://github.com/KOLANICH-tools/antiflash.py)


## License

This software originally comes without a license full text, but within its source code it is written `Licence:     GNU General Public Licence` and https://pypi.org/project/PyChem/ exposes `OSI Approved :: GNU General Public License (GPL)` "Trove classifier". In my opinion, the public release of source code, the license notices in the source code and the Trove classifiers on PyPI clearly carry author's intent to license the software under a `GNU General Public License`.

When the last release of the software was created (2010 year), there used to be 3 versions of GNU GPL in existence: `1`, `2`, and `3`. In GNU GPL license texts from FSF website it used to be said:

1. [`If the Program does not specify a version number of the license, you may choose any version ever published by the Free Software Foundation.`](https://www.gnu.org/licenses/old-licenses/gpl-1.0.en.html)
2. [`If the Program does not specify a version number of this License, you may choose any version ever published by the Free Software Foundation.`](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
3. [`If the Program does not specify a version number of the GNU General Public License, you may choose any version ever published by the Free Software Foundation.`](https://www.gnu.org/licenses/gpl-3.0.en.html)


So we consider this software as licensed under `GNU GENERAL PUBLIC LICENSE Version 3`, SPDX identifier [`GPL-3.0-or-later`](https://spdx.org/licenses/GPL-3.0-or-later.html).

## Modifications

This repo contains a modified version of software. Insignificant changes were applied to original commits in order to reduce "diff noise", reduce size of diffs, simplify code comprehension and debugging.

0. The repo was imported from SourceForge CVS. **Unfortunately only non-TLS access was provided by SF**, which exposes us to MiTM attacks while fetching the source code.
1. Repo was converted into git using [`cvs2git`](https://github.com/mhagger/cvs2svn/tree/75199a08f719ae9843a5c72d304f57ccc6a810c1) and `git fast-import`.
2. Directory layout was changed. `CVSROOT` was removed. The files were transferred into `PyChem` subdir.
3. Source code was bulk-converted into Python 3 using `2to3 -nw`.
4. Indentation was converted into tabs for Python files.
5. `reposurgeon% path rename %^PyChem/(docs|examples)\/(.+)$% \1/\2`
6. `reposurgeon% path rename %^PyChem/(setup_win32\.py|setup_standalone\.py)$% \1`
7. `reposurgeon% path rename %^PyChem/PyChemApp\.py$% PyChem/__main__.py`
8. Reformated using `isort` and `antiflash`.
9. Imports of legacy `wxWidgets` API was replaced with modern ones.
```bash
#!/usr/bin/env bash

rpl -F "lib.customtreectrl" "lib.agw.customtreectrl" "**/*.py"
rpl -F "lib.foldpanelbar" "lib.agw.foldpanelbar" "**/*.py"
rpl -F "lib.buttonpanel" "lib.agw.buttonpanel" "**/*.py"
rpl -F "cluster.treecluster" "treecluster" "**/*.py"
rpl -F "cluster.kcluster" "kcluster" "**/*.py"
rpl -F "wx.AboutBox" "wx.adv.AboutBox" "**/*.py"
rpl -F "wx.AboutDialogInfo" "wx.adv.AboutDialogInfo" "**/*.py"
rpl "\bwx\.NewId\b" "wx.NewIdRef" "**/*.py"
rpl "\bSetToolTipString\b" "SetToolTip" "./**/*.py"
rpl "(\w+)_COLOR" '\1_COLOUR' "./**/*.py"
rpl -F "wx.SashWindow" "wx.adv.SashWindow" "./**/*.py"
rpl -F "wx.SW_3D" "wx.adv.SW_3D" "./**/*.py"
rpl -F "wx.SAVE" "wx.FD_SAVE" "**/*.py"
rpl -F "wx.OVERWRITE_PROMPT" "wx.FD_OVERWRITE_PROMPT" "**/*.py"
rpl -F "InsertStringItem" "InsertItem" "**/*.py"
rpl -F "SetStringItem" "SetItem" "**/*.py"

rpl "(\w+)\.SetFontSizeLegend\(" "\1.fontSizeLegend = (" "**/*.py"
rpl "(\w+)\.SetEnableLegend\(" "\1.enableLegend = (" "**/*.py"
rpl "(\w+)\.SetYSpec\(" "\1.ySpec = (" "**/*.py"
rpl "(\w+)\.SetXSpec\(" "\1.xSpec = (" "**/*.py"
rpl "(\w+)\.SetFontSizeAxis\(" "\1.fontSizeAxis = (" "**/*.py"
rpl "(\w+)\.SetFontSizeTitle\(" "\1.fontSizeTitle = (" "**/*.py"
rpl "(\w+)\.SetEnableZoom\(" "\1.enableZoom = (" "**/*.py"

rpl -F 'scipy.array' 'np.array' "**/*.py"
rpl -F "scipy.io.array_import.str_array" "str_array" "**/*.py"
rpl -F "import scipy.io" "" "**/*.py"
rpl '_attr\["(\w+)"\]' "\1" "**/*.py"
rpl "_attr\['(\w+)'\]" "\1" "**/*.py"
rpl -F ".getchildren()" "" "**/*.py"

rpl "exec\(\"self\.\" \+ item.tag \+ \"\.(\w+)\(\" \+ (.+?)\)'\)" "getByPath(self, item.tag).\1(exec(\2'))" "**/*.py"
rpl "exec\(\"self\.\" \+ item.tag \+ \"\.(\w+)\(\" \+ (.+?)\)\"\)" "getByPath(self, item.tag).\1(exec(\2\"))" "**/*.py"
rpl "exec\(\"(\w+) = self.\" \+ item\.tag\)" "\1 = getByPath(self, item.tag)" "**/*.py"
rpl "exec\('([^\"]+)\[\"' \+ (.+?) \+ '\"\]([^\"]*)'\)" "\1[\2]\3" "**/*.py"
rpl "exec\(\"(\w+) = ET.SubElement\(\" \+ (\w+) \+ ', \"(\w+)\"\)'\)" "\1 = ET.SubElement(locals()[\2], \"\3\")" "**/*.py"
rpl "exec\(\"expSetup\.ResizeGrids\(self\.\" \+ item\.tag \+ \", r, (.+?)\)\"\)" 'expSetup.ResizeGrids(getByPath(self, item.tag), r, \1)' "**/*.py"
rpl "exec\('expSetup\.ResizeGrids\(self\.' \+ item\.tag \+ ', r, (.+?)\)'\)" 'expSetup.ResizeGrids(getByPath(self, item.tag), r, \1)' "**/*.py"
rpl -F "',\"'" "',' + '\"'" "**/*.py"
rpl "exec\(\"(.+?)self\.\" \+ (\w+) \+ \"(.+?)\"\)" "\1getByPath(self, \2)\3" "**/*.py"
rpl "exec\((\w+) \+ '= ET.SubElement\((\w+), \"' \+ (\w+) \+ '\"\)'\)" "locals()[\1] = ET.SubElement(\2, \3)" "**/*.py"
rpl "exec\(\"(\w+) = ET\.SubElement\(\" \+ (\w+) \+ ',\"(\w+)\"\)'\)" "\1 = ET.SubElement(locals()[\2], \"\3\")" "**/*.py"
rpl "exec\((\w+) \+ '([^']+)'\)" "locals()[\1]\2" "**/*.py"
rpl "exec\((\w+) \+ ' = ET\.SubElement\((\w+), \"' \+ (\w+) \+ '\"\)'\)" "locals()[\1] = ET.SubElement(\2, \3)" "**/*.py"
rpl "exec\((\w+) \+ \".(\w+) = ([^\"]+?)self.\" \+ (\w+) \+ \"([^\"]+)\"\)" "locals()[\1].\2 = \3getByPath(self, \4)\5" "**/*.py"
rpl "exec\((\w+) \+ \"([^\"]+?)\"\)" "locals()[\1]\2" "**/*.py"
rpl "exec\(\"(\w+)\" \+ (\w+) \+ ' = ET.SubElement\((\w+), \"' \+ (\w+) \+ '\"\)'\)" "locals()[\"\1\" + \2] = ET.SubElement(\3, \4)" "**/*.py"
rpl "exec\(\"(\w+)\" \+ (\w+) \+ '([^']+)'\)" "locals()[\"\1\" + \2]\3" "**/*.py"
rpl "exec\((\w+) \+ \"([^\"]+)\" \+ (\w+) \+ \"([^\"]+)\"\)" "locals()[name].text = getByPath(self, each).GetValue()" "**/*.py"
rpl "exec\(\"(\w+)\" \+ (\w+) \+ \"([^\"]+)\"\)" "locals()[\"\1\" + \2]\3" "**/*.py"
rpl "exec\('(\w+) = (\w+)\(([^\[]+)\[\"' \+ (\w+) \+ '\"\]([^)]+)\)'\)" "\1 = \2(\3[\4]\5)" "**/*.py"
rpl "exec\('(\w+) = ([\w\.]+)\(' \+ (\w+) \+  ',\"(\w+)\"\)'\)" "\1 = \2(locals()[\3],\"\4\")" "**/*.py"
rpl "exec\(\"(\w+) = ([\w\.]+)\['\" \+ (\w+) \+ \"'\]\"\)" "\1 = \2[\3]" "**/*.py"
rpl "exec\(\"(\w+)\.\" \+ ([^\"]+) \+ \"([^\"]+)\"\)" "getByPath(\1, \2)\3" "**/*.py"
rpl "exec\(\"([\w\.]+)\(((?:[\w]+\.)+)(\w+)\"([^\"]+?)\s*\+\s*\"([^\"]+)\"\)" "\1(getByPath(\2, \"\3\"\4)\5" "**/*.py"
rpl "([a-zA-Z]+)\.," "\1," "**/*.py" # fixes after the previous command

rpl "string\.split\(([^,]+), ([^\)]+)\)" "\1.split(\2)" "./**/*.py"
rpl 'bp\.ButtonPanel\.__init__\(self, parent=prnt, id=-1, text="([\w ]+)", style=bp\.BP_USE_GRADIENT,' 'bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="\1", agwStyle=bp.BP_USE_GRADIENT,' "./**/*.py"
rpl 'bp\.ButtonPanel\.__init__\(self, parent=prnt, id=-1, text="GA-" \+ self\.type, style=bp\.BP_USE_GRADIENT,' 'bp.ButtonPanel.__init__(self, parent=prnt, id=-1, text="GA-" + self.type, agwStyle=bp.BP_USE_GRADIENT,' "./**/*.py"
rpl "string\.lower\(([^\)]+)\)" "\1.lower()" "./**/*.py"

rpl -F 'string.join(("The following error occured:\n\n", error), "")' '"".join(("The following error occured:\n\n", error))' "./**/*.py"
rpl -F 'string.join((confmat, "\n"), "")' '"".join((confmat, "\n"))' "./**/*.py"
rpl -F 'string.join((confmat, "\t", str(i + 1)), "")' '"".join((confmat, "\t", str(i + 1)))' "./**/*.py"
rpl -F 'string.join((centres, "% .2f" % centroids[i, j], "\n"), "")' '"".join((centres, "% .2f" % centroids[i, j], "\n"))' "./**/*.py"
rpl -F 'string.join((centres, str(i + 1), "\t\t", "% .2f" % centroids[i, j], "\t"), "")' '"".join((centres, str(i + 1), "\t\t", "% .2f" % centroids[i, j], "\t"))' "./**/*.py"
rpl -F 'string.join((centres, str(i + 1), "\t\t", "% .2f" % centroids[i, j], "\t"), "")' '"".join((centres, str(i + 1), "\t\t", "% .2f" % centroids[i, j], "\t"))' "./**/*.py"
rpl -F 'string.join(("Principal component", str(i)), " ")' '" ".join(("Principal component", str(i)))' "./**/*.py"
rpl -F 'string.join(("Extracting factor...", str(xi + 1)), " ")' '" ".join(("Extracting factor...", str(xi + 1)))' "./**/*.py"
rpl -F 'string.join(("*/", workspace), "")' '"".join(("*/", workspace))' "./**/*.py"
rpl -F 'string.join((centres, "\n"), "")' '"".join((centres, "\n"))' "./**/*.py"

rpl -F 'string.join((str(Var), "vars"), " ")' '" ".join((str(Var), "vars"))' "./**/*.py"
rpl -F 'string.join((confmat, "\t", str(confarr[i, j])), "")' '"".join((confmat, "\t", str(confarr[i, j])))' "./**/*.py"
rpl -F 'string.join(("Variable", str(Vars + varFrom)), " ")' '" ".join(("Variable", str(Vars + varFrom)))' "./**/*.py"
rpl -F 'string.join(("Run", str(Runs + 1)), " ")' '" ".join(("Run", str(Runs + 1)))' "./**/*.py"
rpl -F 'string.join(("Generation", str(count)), " ")' '" ".join(("Generation", str(count)))' "./**/*.py"
rpl -F 'string.join((confmat, str(i + 1), "\t\t", str(confarr[i, j])), "")' '"".join((confmat, str(i + 1), "\t\t", str(confarr[i, j])))' "./**/*.py"
rpl -F 'string.join((centres, "% .2f" % centroids[i, j], "\t"), "")' '"".join((centres, "% .2f" % centroids[i, j], "\t"))' "./**/*.py"
rpl -F 'string.join((centres, "\t", str(i + 1)), "")' '"".join((centres, "\t", str(i + 1)))' "./**/*.py"

rpl -F 'string.join(("PLS Predictions:", str(_attr["factors"] + 1), "factors, RMS(Indep. Test)", "%.2f" % _attr["RMSEPT"]), " ")' '" ".join(("PLS Predictions:", str(_attr["factors"] + 1), "factors, RMS(Indep. Test)", "%.2f" % _attr["RMSEPT"]))' "./**/*.py"
rpl -F 'string.join((title, "\n-----------------------\n\n", "No. clusters\t\tError\t\tNo. optimal soln.\n", "----------------\t\t--------\t\t------------------------\n", str(max(self.clusterid) + 1), "\t\t\t", "% .2f" % error, "\t\t", str(nfound)), "")' '"".join((title, "\n-----------------------\n\n", "No. clusters\t\tError\t\tNo. optimal soln.\n", "----------------\t\t--------\t\t------------------------\n", str(max(self.clusterid) + 1), "\t\t\t", "% .2f" % error, "\t\t", str(nfound)))' "./**/*.py"
rpl -F 'string.join((summary, centres, confmat), "")' '"".join((summary, centres, confmat))' "./**/*.py"
rpl -F 'string.join((str(vars + _attr["varfrom"]), " variables"), "")' '"".join((str(vars + _attr["varfrom"]), " variables"))' "./**/*.py"
rpl -F 'string.join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabelsfull"], (len(self.data["indlabelsfull"]),)), RunLabel)), " ", "%.2f" % (gaScoreList[idx[(vars * (_attr["runs"] + 1)) + runs]])), "")' '"".join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabelsfull"], (len(self.data["indlabelsfull"]),)), RunLabel)), " ", "%.2f" % (gaScoreList[idx[(vars * (_attr["runs"] + 1)) + runs]])))' "./**/*.py"
rpl -F 'string.join((axis, yL), " ")' '" ".join((axis, yL))' "./**/*.py"
rpl -F 'string.join((axis, str(col1 + 1)), " ")' '" ".join((axis, str(col1 + 1)))' "./**/*.py"
rpl -F 'string.join((axis, xL), " ")' '" ".join((axis, xL))' "./**/*.py"
rpl -F 'string.join((axis, str(col2 + 1)), " ")' '" ".join((axis, str(col2 + 1)))' "./**/*.py"

rpl -F 'string.replace(data, "]]", "")' 'data.replace("]]", "")' "./**/*.py"
rpl -F 'string.replace(data, "   \n                ", "   ")' 'data.replace("   \n                ", "   ")' "./**/*.py"
rpl -F 'string.replace(data, "\n            ", "   ")' 'data.replace("\n            ", "   ")' "./**/*.py"
rpl -F 'string.replace(data, "]\n [ ", "\n")' 'data.replace("]\n [ ", "\n")' "./**/*.py"
rpl -F 'string.replace(str(self.data["raw"]), "[[ ", "")' 'str(self.data["raw"]).replace("[[ ", "")' "./**/*.py"

rpl -F "string.join((\".//Workspaces/\",workspace),'')" '"".join((".//Workspaces/",workspace))' "./**/*.py"
rpl -F 'string.join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabelsfull"], (len(self.data["indlabelsfull"]),)), RunLabel)), " ", "%.2f" % (gaScoreList[Count + mch])), "")' '"".join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabelsfull"], (len(self.data["indlabelsfull"]),)), RunLabel)), " ", "%.2f" % (gaScoreList[Count + mch])))' "./**/*.py"
rpl -F 'string.join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabels"], (len(self.data["indlabels"]),)), RunLabel)), " " "%.2f" % (gaScoreList[Count + mch])), "")' '"".join(("#", str(IterCount + 1), " ", str(scipy.take(scipy.reshape(self.data["indlabels"], (len(self.data["indlabels"]),)), RunLabel)), " " "%.2f" % (gaScoreList[Count + mch])))' "./**/*.py"
rpl -F 'string.join(("PLS Model:", str(factors + 1), "factors, RMS(Indep. Test)", "%.3f" % RMSEPT), " ")' '" ".join(("PLS Model:", str(factors + 1), "factors, RMS(Indep. Test)", "%.3f" % RMSEPT))' "./**/*.py"
rpl -F 'string.join(("PLS Predictions:", str(factors + 1), "factors, RMS(Indep. Test)", "%.3f" % RMSEPT), " ")' '" ".join(("PLS Predictions:", str(factors + 1), "factors, RMS(Indep. Test)", "%.3f" % RMSEPT))' "./**/*.py"
rpl -F 'string.join(("Extracting factor...", str(x + 1)), " ")' '" ".join(("Extracting factor...", str(x + 1)))' "./**/*.py"
#rpl -F 'string.join((title, "\n-------------\n\n", "No. clusters\t\tError\t\tNo. optimal soln.\n", "----------------\t\t--------\t\t------------------------\n", str(max(self.clusterid) + 1), "\t\t\t", "% .2f" % error, "\t\t", str(nfound)), "")' '"".join((title, "\n-------------\n\n", "No. clusters\t\tError\t\tNo. optimal soln.\n", "----------------\t\t--------\t\t------------------------\n", str(max(self.clusterid) + 1), "\t\t\t", "% .2f" % error, "\t\t", str(nfound)))' "./**/*.py"
rpl -F 'string.replace(data, "	\n		  ", "	 ")' 'data.replace("	\n		  ", "	 ")' "./**/*.py"
rpl -F 'string.replace(data, "\n		   ", "	  ")' 'data.replace("\n		   ", "	  ")' "./**/*.py"
rpl -F 'string.replace(data, "  ", "	  ")' 'data.replace("  ", "	  ")' "./**/*.py"
rpl -F "'%.2f' %tstgerr),'')" "'%.2f' %tstgerr))" "./**/*.py"
rpl -F "OlsResults = string.join((" 'OlsResults = "".join((' "./**/*.py"
```
